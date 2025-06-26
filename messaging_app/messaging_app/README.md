# Readme

- create kuberenetes app secretes with:
  minikube kubectl -- create secret generic app-secrets \
   --from-literal=MYSQL_DATABASE=<your sql db> \
   --from-literal=MYSQL_USER=<Your sql user name> \
   --from-literal=MYSQL_PASSWORD=<your sql user password> \
   --from-literal=MYSQL_ROOT_PASSWORD=<your sql root password> \
   --from-literal=DB_HOST=<db host>\
   --from-literal=DB_PORT=<port>

- Load local django image into minikube
  eval $(minikube docker-env)
  docker build -t messaging_app-web:latest .

#### On local

- do not create namespace with:
  kubectl create namespace messaging

## deploy

kubectl apply -f deployment.yaml

# View pods in namespace

- kubectl get pods -n messaging or kubectl get pods --namespace messaging
