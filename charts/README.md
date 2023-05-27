# Fiesta Helm Charts

This application charts installs the entire Fiesta system as Helm installation.


## Resources

|    kind    | chart                                                      | purpose                                                                                             |
|:----------:|------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Deployment | [`web-deployment.yaml`](./templates/web-deployment.yaml)   | runs the Django application pods, each with main Django container and nginx sidecar proxy container |
|  Service   | [`web-svc.yaml`](./templates/web-svc.yaml)                 | routes requests to deployed application                                                             |
|    Job     | [`web-migrate-job.yaml`](./templates/web-migrate-job.yaml) | post install hook to migrate Django database                                                        |
|   Secret   | [`web-secret.yaml`](./templates/web-secret.yaml)           | database credentials, generated secret key, etc                                                     |
| ConfigMap  | [`web-config.yaml`](./templates/web-config.yaml)           | dynamic configuration for application                                                               |
|  Ingress   | [`ingress.yaml`](./templates/ingress.yaml)                 | ingress LoadBalancer configuration for cloud provider                                               |


## Values

Part of the values are provided during deploy:

| key                        | meaning                              |
|----------------------------|--------------------------------------|
| `web.repository`           | repository of web application image  |
| `web.tag`                  | tag of web application image         |
| `proxy.repository`         | repository of proxy sidecar  image   |
| `proxy.tag`                | tag of proxy sidecar image           |
| `proxy.repository`         | repository of proxy sidecar  image   |
| `ingress.certContactEmail` | contact email for Let's Encrypt ACME |
| `secrets.databaseUrl`      | application database credentials URL |
| `secrets.s3.keyId`         | S3 object storage KEY_ID             |
| `secrets.s3.accessKey`     | S3 object storage ACCESS_KEY         |
| `secrets.s3.regionName`    | S3 object storage region name        |
| `secrets.s3.bucketName`    | S3 object storage bucket name        |
