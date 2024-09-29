#!/bin/sh

# stop on errors
set -e

if [ $# -ne 4 ]; then
    echo "Usage: ./hailo15_customer_key_sign.sh [cryptocell-312-runtime-path] [root-of-trust-keypair] [content-pubkey] [output_certificate_name]"
    exit 1
fi

# get script directory
script_dir=$(realpath $(dirname "$0"))

# parse arguments
cc_runtime_path=$(realpath $1)
rot_keypair=$(realpath $2)
content_pubkey=$(realpath $3)
output_certificate_name=$(realpath $4)

# temporary files used during the signing process
temporary_directory=$(mktemp -d)
certificate_config_file_full_hbk="${temporary_directory}/certificate_config_full_hbk.txt"
certificate_config_file_hbk0="${temporary_directory}/certificate_config_hbk0.txt"
certificate_filename_full_hbk="${temporary_directory}/full_hbk_cert.bin"
certificate_filename_hbk0="${temporary_directory}/hbk0_cert.bin"
rot_pubkey_copy="${temporary_directory}/rot_pubkey_copy.pem"
content_pubkey_copy="${temporary_directory}/content_pubkey_copy.pem"

# change to the temporary directory, so that we can cleanup the temporary files easily
cd ${temporary_directory}

# extract the public key from the root-of-trust keypair
openssl rsa -in ${rot_keypair} -pubout -out ${rot_pubkey_copy}

# extract the public key from the content pubkey (make sure we compare two files produced by the same openssl)
openssl rsa -pubin -in ${content_pubkey} -pubout -out ${content_pubkey_copy}

# verify that the root-of-trust public key and content public key are different
if cmp -s ${rot_pubkey_copy} ${content_pubkey_copy}; then
    echo "Error: Root-of-trust public key and content public key are the same."
    echo "       Using the same key as root-of-trust and content key is a security issue. You must use different keys."
    exit 1
fi

# generate certificate configuration files for full HBK and HBK0 from template
rot_keypair=${rot_keypair} content_pubkey=${content_pubkey} cert_package_name=${certificate_filename_full_hbk} hbk_id=2 envsubst \
    < ${script_dir}/hailo15_key_certificate_config_template.txt > ${certificate_config_file_full_hbk}
rot_keypair=${rot_keypair} content_pubkey=${content_pubkey} cert_package_name=${certificate_filename_hbk0} hbk_id=0 envsubst \
    < ${script_dir}/hailo15_key_certificate_config_template.txt > ${certificate_config_file_hbk0}

# sign the binary using the cryptocell library
python3 ${cc_runtime_path}/utils/bin/cert_key_util.py ${certificate_config_file_full_hbk} -cfg_file ${cc_runtime_path}/utils/src/proj.cfg
python3 ${cc_runtime_path}/utils/bin/cert_key_util.py ${certificate_config_file_hbk0} -cfg_file ${cc_runtime_path}/utils/src/proj.cfg

cat ${certificate_filename_full_hbk} ${certificate_filename_hbk0} > ${output_certificate_name}

# cleanup temporary files
rm -rf ${temporary_directory}
