# #!/bin/sh
# # Resolve the DNS name and set it as an environment variable
# export REACT_APP_PYTHON_SERVER_URL=$(getent hosts EXPRESS_SERVER_SERVICE_SERVICE_HOST | awk '{ print $1 }')

# # Check if the variable is set and not empty
# if [ -z "$REACT_APP_PYTHON_SERVER_URL" ]; then
    # echo "Could not resolve DNS for EXPRESS_SERVER_SERVICE_SERVICE_HOST"
    # exit 1
# fi


#!/bin/sh

# Start supervisor which will launch both Gunicorn and Nginx
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf



# Start nginx in the foreground
nginx -g 'daemon off;'