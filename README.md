### proxy-server-g3
1. UPDATE ENV
 - apt-get update
 - apt-get install -y git build-essential libpcre3 libpcre3-dev libssl-dev libtool autoconf apache2-dev libxml2-dev libcurl4-openssl-dev automake pkgconf

2. SETUP PROXY SERVER
 - cd /usr/src
 - git clone https://github.com/athenakimhue/proxy-server-g3.git
 - cd /usr/src/proxy-server-g3/ModSecurity/
 - chmod 777 autogen.sh
 - ./autogen.sh  && ./configure --enable-standalone-module --disable-mlogc && make
 - cd /usr/src/proxy-server-g3/
 - chmod 777 configure
 - ./configure --user=www-data --group=www-data --add-module=/usr/src/proxy-server-g3/ModSecurity/nginx/modsecurity  --add-module=/usr/src/proxy-server-g3/cookie_flag_module --with-http_ssl_module && make && make install
 - cp /usr/src/proxy-server-g3/conf/modsec_includes.conf /usr/local/nginx/conf/
 && cp /usr/src/proxy-server-g3/conf/modsecurity.conf /usr/local/nginx/conf/
 && cp /usr/src/proxy-server-g3/conf/unicode.mapping /usr/local/nginx/conf/
 && cp -r /usr/src/proxy-server-g3/conf/owasp-modsecurity-crs /usr/local/nginx/conf/
 && cp /usr/src/proxy-server-g3/owasp-modsecurity-crs/crs-setup.conf /usr/local/nginx/conf/owasp-modsecurity-crs/



 
