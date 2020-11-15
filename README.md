# project_provisioning

This is a sample appengine deployment that will receive provision projects according to provided parameters.

To protect the deployment, enable IAP and create a service account to authenticate against the endpoint.
See documentation here for more details https://cloud.google.com/iap/docs/app-engine-quickstart#enabling_iap

Do note that the service account which appengine running needs to be given project creator role on the folders which are allowed to be created under.

The service account also requires Billing Account User on the billing account to be attached to the project.

## Deployment
To deploy the following endpoint
1. gcloud init
1. gcloud app create
    1. choose region nearest to the users
1. gcloud app deploy