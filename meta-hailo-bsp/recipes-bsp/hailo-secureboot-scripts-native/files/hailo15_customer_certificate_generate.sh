#!/bin/sh

# stop on errors
set -e

if [ $# -ne 4 ]; then
    echo "Usage: ./hailo15_customer_certificate_generate.sh [cryptocell-312-runtime-path] [key-certificate] [customer-keypair] [output_customer_certificate]"
    exit 1
fi

# get script directory
script_dir=$(realpath $(dirname "$0"))

# parse arguments
cc_runtime_path=$(realpath $1)
key_certificate=$(realpath $2)
customer_keypair=$(realpath $3)
output_customer_certificate=$(realpath $4)

# temporary files used during the signing process
temporary_directory=$(mktemp -d)
customer_pubkey="${temporary_directory}/customer_pubkey.pem"
hash_file="${temporary_directory}/hash_file.bin"
content_certificate_file="${temporary_directory}/content_certificate.bin"
certificate_config_file="${temporary_directory}/certificate_config.txt"
images_table_file="${temporary_directory}/images_table.txt"

# in sh, printf is an internal command, and we want to use the external printf command
PRINTF=$(which printf)

# change to the temporary directory, so that we can cleanup the temporary files easily
cd ${temporary_directory}

# extract the public key from the root-of-trust keypair
openssl rsa -in ${customer_keypair} -pubout -out ${customer_pubkey}

python3 ${cc_runtime_path}/utils/bin/hbk_gen_util.py -key ${customer_pubkey} -hash_format SHA256 -endian B

for hex_val in $(cat prim_key_hash.txt | sed "s/,/ /g")
do
    uint32be_val=$($PRINTF "0x%08x" $hex_val)
    $PRINTF "%b" $($PRINTF '\\x%02x\\x%02x\\x%02x\\x%02x' \
                    $(((${uint32be_val} & 0xFF000000) >> 24)) \
                    $(((${uint32be_val} & 0xFF0000) >> 16)) \
                    $(((${uint32be_val} & 0xFF00) >> 8)) \
                    $((${uint32be_val} & 0xFF))) >> ${hash_file}
done

# create images table from template
image=${hash_file} load_address=0x60000000 binary_size=0x20 envsubst < ${script_dir}/hailo15_images_table_template.txt > ${images_table_file}

# create the certificate configuration file from template
cert_keypair=${customer_keypair} images_table=${images_table_file} content_certificate=${content_certificate_file} envsubst \
    < ${script_dir}/hailo15_content_certificate_config_template.txt > ${certificate_config_file}

# sign the binary using the cryptocell library
python3 ${cc_runtime_path}/utils/bin/cert_sb_content_util.py ${certificate_config_file} -cfg_file ${cc_runtime_path}/utils/src/proj.cfg

# generate the customer certificate by concatenating the key certificate, content certificate and hash file
cat ${key_certificate} ${content_certificate_file} ${hash_file} > ${output_customer_certificate}

# cleanup temporary files
rm -rf ${temporary_directory}
