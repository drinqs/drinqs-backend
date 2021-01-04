SET env=%{ENV:-dev}

case $env in
  "dev" )
    SET COMPOSE_FILE="docker-compose.yml:docker-compose.sync.yml:docker-compose.development.yml"
    if [ -e "docker-compose.user.yml" ]
    then
      SET COMPOSE_FILE=${COMPOSE_FILE}:docker-compose.user.yml
    fi
  "test" )
    SET COMPOSE_PROJECT_NAME=drinqs-test
    SET COMPOSE_FILE="docker-compose.yml:docker-compose.sync.yml:docker-compose.test.yml"
    ;;
  "prod" )
    SET COMPOSE_PROJECT_NAME=drinqs-prod
    SET COMPOSE_FILE="docker-compose.yml"
esac


docker-compose "%*"
