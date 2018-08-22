# MLT Features

## Templates

* [experiments](../mlt-templates/experiments): Runs hyperparameter experiments for a demo job.
* [hello-world](../mlt-templates/hello-world): A TensorFlow python HelloWorld example run through Kubernetes Jobs.
* [pytorch](../mlt-templates/pytorch): Sample distributed application taken from http://pytorch.org/tutorials/intermediate/dist_tuto.html
* [pytorch-distributed](../mlt-templates/pytorch-distributed): A distributed PyTorch MNIST example run using the pytorch-operator.
* [tensorboard](../mlt-templates/tensorboard): A TensorBoard service in Kubernetes cluster.
* [tf-dist-mnist](../mlt-templates/tf-dist-mnist): A distributed TensorFlow MNIST model which designates worker 0 as the chief.
* [tf-distributed](../mlt-templates/tf-distributed): A distributed TensorFlow matrix multiplication run through the TensorFlow Kubernetes Operator.
* [horovod](../mlt-templates/horovod): A distributed model training using horovod and openmpi.

## Commands

* [mlt templates](#mlt-templates)
* [mlt init](#mlt-init)
* [mlt config](#mlt-config)
* [mlt build](#mlt-build)
* [mlt deploy](#mlt-deploy)
* [mlt status (alpha)](#mlt-status-alpha)
* [mlt logs (alpha)](#mlt-logs-alpha)
* [mlt events (alpha)](#mlt-events-alpha)
* [mlt undeploy](#mlt-undeploy)
* [mlt update-template (alpha)](#mlt-update-template-alpha)
* [mlt sync](#mlt-sync)

### mlt templates


```
mlt (template | templates) list [--template-repo=<repo>]
```

This commands lists the available templates in the specified template
repository.  The name of each template is listed along with a
description.

| Option | Description |
|--------|-------------|
| `--template-repo=<repo>` | Git URL of template repository or a path to a local `mlt` directory.  Default: https://github.com/IntelAI/mlt |

### mlt init

```
  mlt init [--template=<template> --template-repo=<repo>]
      [--registry=<registry> --namespace=<namespace>]
      [--skip-crd-check] [--enable-sync] <name>
```

The `mlt init` command is used for initializing a new application based
one of the available templates.  Select the template that most closely
resembles your use case.  This command will create a directory with the
name provided, which contains all the files necessary to build and
deploy the application.

| Option | Description | Default |
|--------|-------------|---------|
| `--template=<template>` | Template name for app initialization. | hello-world |
| `--template-repo=<repo>` | Git URL of template repository or a path to a local `mlt` directory. | https://github.com/IntelAI/mlt |
| `--registry=<registry>` | Container registry to use.  | Attempt to use gcloud |
| `--namespace=<namespace>` | Kubernetes namespace to use. | Use namespace identical to username |
| `--skip-crd-check` | Skip checking for the cluster for CRDs required by the template | False |
| `--enable-sync` | Enable future syncing capability for the app/template code| False |

| Positional Argument | Description |
|---------------------|-------------|
| `<name>` | Name of your application/project to initialize. |

### mlt config

```
  mlt config list
```

This command lists the configuration parameters for the current project
directory.

```
  mlt config set <name> <value>
```

| Positional Argument | Description |
|---------------------|-------------|
| `<name>` | Name of the configuration parameter to set. |
| `<value>` | Value of the configuration parameter to set. |

```
  mlt config remove <name>
```

| Positional Argument | Description |
|---------------------|-------------|
| `<name>` | Name of the configuration parameter to remove. |

### mlt build

```
  mlt build [--watch] [-v | --verbose]
```

This command builds a local image for the current project directory.

| Option | Description | Default |
|--------|-------------|---------|
| `--watch` | The terminal window watches the project directory, and rebuilds the image when a change is detected.  Use `ctrl-c` to stop the `--watch` session.  | False |
| `-v` `--verbose` | Prints the logs as the image builds.  This option is recommended for long running builds. |

### mlt deploy

```
  mlt deploy [--no-push] [-i | --interactive] [-l | --logs]
      [--retries=<retries>] [--skip-crd-check]
      [--since=<duration>]
```

The `mlt deploy` command pushes the last image that was built for the
current project to the container registry and then deploys the job to
the cluster using Kubernetes.

| Option | Description | Default |
|--------|-------------|---------|
| `--no-push` | Skips the image push and deploys the project to Kubernetes using the same image from your last run. | False |
| `-i` `--interactive` | Rewrites container command to infinite sleep, and then drops the user into `kubectl exec` shell.  Adds a `debug=true` label for easy discovery later. If you have more than 1 template yaml, specify which file you'd like to deploy nteractively as the `kube_spec`. `kube_spec` is only used with this flag. | False |
| `-l` `--logs` | After the job is deployed, watch for the pods to be running, then start tailing the logs. | False |
| `--retries=<retries>` | Number of times to retry waiting for pods to come up for `--logs` or `--interactive`.  Waits 1 second between retrying. | 10 |
| `--since` | Returns logs newer than a relative duration like 10s, 1m, or 2h.  Only used in conjunction with the `--logs` option. | 1m |
| `--skip-crd-check` | Skip checking for the cluster for CRDs required by the template. | False |

| Positional Argument | Description |
|---------------------|-------------|
| `<kubespec>` | Used to specify the file that you want to deploy interactively, if you have more than one template yaml. Only used with the `--interactive` flag. |

### mlt status (alpha)

```
  mlt status
```

The `mlt status` command displays the job/pod status for the last job
that was deployed for the current project directory.

### mlt logs (alpha)

```
  mlt (log | logs) [--since=<duration>] [--retries=<retries>]
```

The `mlt log` command waits for pods to start running, then tails the
logs for those pods using `kubetail`.

| Option | Description | Default |
|--------|-------------|---------|
| `--retries=<retries>` | Number of times to retry waiting for pods to come up for `--logs` or `--interactive`.  Waits 1 second between retrying. | 10 |
| `--since` | Returns logs newer than a relative duration like 10s, 1m, or 2h.  Only used in conjunction with the `--logs` option. | 1m |

### mlt events (alpha)

```
  mlt events
```

This command displays the Kubernetes events related to the last job that
was deployed for the current project directory.

### mlt undeploy

```
  mlt undeploy [--all] [--job-name=<name>]
```

This command undeploys the jobs that were deployed from the current
project directory.  This frees resources in Kubernetes by deleting the
associated job, pods, deployments, etc.

| Option | Description | Default |
|--------|-------------|---------|
| `--all` | Undeploys all the jobs that were deployed from the current project directory.|
| `--job-name=<name>` | The name of the job to undeploy. |

### mlt update-template (alpha)

```
   mlt update-template
```

The `mlt update-template` command checks for updates of the template
used to create the curent project.  If there have been updates to the
template, those updates are pulled and merged with any local changes
that were made in the current project directory.  `git` is used to merge
the updated templates.  A list of file conflicts will be listed, if
there were any conflicts that need to be manually resolved.  A backup of
the original project directory is saved before the update, in case the
user wants to revert back to their original code.

### mlt sync

```
   mlt sync (create | reload | delete)
```

This command is used for syncing local file/folder changes with the deployed app.
`mlt sync` and it's subcommands are only available only if the app is initialized with `--enable-sync`.<br/>
Once the app is deployed, calling `mlt sync create` sets up the local directory to be synced with the
pods of running app which in turn restarts the containers every time changes are made to local files/folders
of the app code. This command only needs to run once.<br/>
`mlt sync reload` restarts the `sync` agent after a local system reboot or long inactivity
(default is 1 hour) or any other activity that causes `sync` agent to die.<br/>
`mlt sync delete` tears down syncing setup and stops syncing local code changes with remote pods.
This command only need to run once.<br/>
To ignore files and folders from syncing, they should be added to `.stignore` file.


## Upcoming Features
* TBD
