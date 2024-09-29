#!/bin/sh

# stop on errors
set -e

if [ $# -ne 5 ]; then
    echo "Usage: ./hailo15_scu_image_sign.sh [cryptocell-312-runtime-path] [key-certificate] [customer-keypair] [input_binary_name] [output_signed_binary_name]"
    exit 1
fi

# get script directory
script_dir=$(realpath $(dirname "$0"))

# parse arguments
cc_runtime_path=$(realpath $1)
key_certificate=$(realpath $2)
customer_keypair=$(realpath $3)
input_binary=$(realpath $4)
output_signed_binary=$(realpath $5)

# temporary files used during the signing process
temporary_directory=$(mktemp -d)
images_table_file="${temporary_directory}/images_table.txt"
content_certificate_file="${temporary_directory}/content_certificate.bin"
certificate_chain_file="${temporary_directory}/certificate_chain.bin"
certificate_config_file="${temporary_directory}/certificate_config.txt"
firmware_header="${temporary_directory}/firmware_header.bin"
firmware_code="${temporary_directory}/firmware_code.bin"
padded_firmware_code="${temporary_directory}/padded_firmware_code.bin"

# change to the temporary directory, so that we can cleanup the temporary files easily
cd ${temporary_directory}

# check if input binary is big enough
if [ $(stat -c "%s" "${input_binary}") -le 24 ]; then
    echo "Input binary must be greater than 24 bytes"
    exit 1
fi

# check if input binary size is divisible by 4
if [ $(( $(stat -c "%s" "${input_binary}") % 4 )) -ne 0 ]; then
    echo "Input binary size must be divisible by 4"
    exit 1
fi

# extract the firmware header
dd if=${input_binary} of=${firmware_header} bs=1 count=24

# extract the firmware code
dd if=${input_binary} of=${firmware_code} bs=1 skip=24

# the cryptocell library expects binaries padded to 4 bytes
# so we have to add padding in case the binary is not aligned to 4 byte
dd if=${firmware_code} of=${padded_firmware_code} ibs=4 conv=sync

# calculate the size of the padded input binary
padded_firmware_code_size=$(printf "0x%x" `stat -c "%s" "${padded_firmware_code}"`)

# create images table from template
# a signed binary consists of 2 signed entries: the firmwware code and the firmware header
image=${padded_firmware_code} load_address=0x20000 binary_size=${padded_firmware_code_size} envsubst \
    < ${script_dir}/hailo15_images_table_template.txt > ${images_table_file}
image=${firmware_header} load_address=0x88000 binary_size=0x18 envsubst \
    < ${script_dir}/hailo15_images_table_template.txt >> ${images_table_file}

# create the certificate configuration file from template
cert_keypair=${customer_keypair} images_table=${images_table_file} content_certificate=${content_certificate_file} envsubst \
    < ${script_dir}/hailo15_content_certificate_config_template.txt > ${certificate_config_file}

# sign the binary using the cryptocell library
python3 ${cc_runtime_path}/utils/bin/cert_sb_content_util.py ${certificate_config_file} -cfg_file ${cc_runtime_path}/utils/src/proj.cfg

# prepare certificate chain
python3 ${script_dir}/prepare_scu_firmware_certificate_chain.py ${key_certificate} ${content_certificate_file} ${certificate_chain_file}

# generate the signed binary by concatenating the firmware with the certificate chain
cat ${input_binary} ${certificate_chain_file} > ${output_signed_binary}

# cleanup temporary files
rm -rf ${temporary_directory}
