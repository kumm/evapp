WISE keys
-------------

ssh-keygen -m pem -f ./config/wise.pem
chmod 600 ./config/wise.pem
mv ./config/wise.pem.pub ./config/wise.pub
ssh-keygen -f ./config/wise.pub -m 'PEM' -e > ./config/wise.pub.pem
rm ./config/wise.pub
