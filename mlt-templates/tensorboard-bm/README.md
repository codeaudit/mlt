# TensorBoard MLT Application for Bare Metal Clusters

A TensorBoard service in Kubernetes Bare Metal cluster.

This template requires configuration of both user domain and Tensorflow job logs path.
The command below shows how to update the log directory value in `k8s-templates/tbjob.yaml`.

`mlt template_config set template_parameters.logdir /tmp` , and
`mlt template_config set template_parameters.domain my-domain.com`

TensorBoard template works with different storage sources, and it's the user's responsibility to allow the TensorBoard service to access the logs location.

This template assumes that `jq` is installed. `jq` is used while launching TensorBoard to query the service host.

### Steps to launch TensorBoard service using TensorBoard MLT template:

1. Create a TensorBoard application using the TensorBoard MLT template.
`mlt init tensorboard-app --template=tensorboard-bm --namespace=<value> --registry=<value>`

`cd tensorboard-app` :

2. Set TensorBoard `logdir` and `domain`.
`mlt template_config set template_parameters.logdir <value>` and
`mlt template_config set template_parameters.domain <value>`

3. Create the application image.
`mlt build`

4. Deploy TensorBoard service.
`mlt deploy`,
which deploys the TensorBoard service and launches the local browser with `http://<service-name>.domain`.
It might take few seconds for the service to be up and running, so reload the page if TensorBoard did not open right away.

7. Finally, when done, a user can delete the running TensorBoard service
`mlt undeploy`.
