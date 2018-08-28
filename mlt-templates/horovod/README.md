# Distributed TensorFlow using Horovod

A distributed model training using horovod and openmpi.

This template deploys horovod model on kubernetes using [kubeflow openmpi](https://github.com/kubeflow/kubeflow/blob/master/kubeflow/openmpi/README.md).

Template structure as follows:

* deploy.sh - Actual script which deploys your model to k8.
* Dockerfile.cpu - Used when `gpus=0`
* Dockerfile.gpu - Used when `gpus > 0`
* main.py - Sample tensorflow_mnist model using horovod. (Replace content in this file with your own model content. *Note:* do not change filename)
* Makefile - Contains targets for your template
* requirements.txt - List tensorflow versions you want to use (Make sure to use right Nvidia/Cuda versions
        because they are tightly coupled with tensorflow version)


### Volume support

If you want to mount your data for training purposes, please set `ks param` in your `deploy.sh` script.
To use that data, you need to add {extra parameters here} to the `template_parameters` field which you
can access via `mlt template_config`.


```
    # Location of your training dataset. In this scenario, we already have RAW data converted to .npy files at this location
    "base_dir": "/var/datasets/unet/vck-resource-8fd827a8-809a-11e8-b982-0a580a480bd4",

    # Location where output results should be stored. In this we are storing at same location as base_dir with output sub_dir.
    "output_path": "/var/datasets/unet/vck-resource-8fd827a8-809a-11e8-b982-0a580a480bd4"

```
