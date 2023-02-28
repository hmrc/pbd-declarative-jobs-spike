
# pbd-declarative-jobs-spike

This repo captures the output of an HMRC MDTP Build & Deploy (B&D) team hackday spike. It contains a proof of concept for translating high level repository metadata into [jenkins-job-builders](https://github.com/hmrc/jenkins-job-builders) style DSL for provisioning CI/CD jobs.

## Purpose

We have received feedback from our colleagues in PlatDocs that MDTP service team engineers sometimes find the process of defining groovy based job configuration difficult. Even when advice is provided, it can be hard to handle all of the various edge cases.

Further, existing definitions in our internal [build-jobs repository](https://github.com/hmrc/build-jobs) are often implemented in a plethora of different ways. This can make it difficult for teams to understand what pattern they should be following, given that an exemplar might differ substantially differ from other implementations.

We're also looking at streamlining the process for creating new microservices on the MDTP platform. It feels to us that insisting that teams explicitly provide us with CI/CD job definitions is perhaps redundant when it's something they need and could be implicit.

Lastly, our current implementation ties our service team customers quite closely into the Jenkins ecosystem. By providing service teams with something more abstract, we can potentially ease the process of migrating to a different CI/CD service in future.

To that end, we have decided to use some hackday time to explore the idea of automatically generating job DSL via abstract service metadata that is written to a `repository.yaml` file in the root of the service repository. This is a pattern which is gaining popularity across platform teams for driving various behaviours.

## Installation

You require at least version `3.9` of python and poetry installed as prerequisites.

To install the application dependencies in an isolated virtual environment, run:

```bash
$ poetry install
```

## Usage

Make changes to the sample [repository.yaml](repository_yaml/my-lovely-service/repository.yaml) that reflect the characteristics of the code in the repository.

For example, a public sbt-microservice that requires mongo and is automatically deployed to the `qa` and `staging` environments would have a `repository.yaml` like:

```yaml
repoVisibility: public_0C3F0CE3E6E6448FAD341E7BFA50FCD333E06A20CFF05FCACE61154DDBBADF71
repoType: sbt_frontend_microservice
namespace: My Lovely Team/My Lovely Service Group
environments:
    - qa
    - staging
mongo: true
```

In real life, we would catch changes to this configuration in the B&D API via GitHub events and fetch the content. For the purposes of this spike, we just run the parser manually, which loads the config from the repo via a hardcoded path:

```bash
poetry run parse-yaml
```

This results in a couple of additions to the [build](build/) directory. The `dsl_4489098a692c6e51ab4836f9b3bbc9cc.groovy` contains the definition for the required folder the jobs will be created in:

```groovy
import javaposse.jobdsl.dsl.DslFactory

import uk.gov.hmrc.buildjobs.domain.builder.TeamFolderBuilder

new TeamFolderBuilder("My Lovely Team")
   .withDisplayName("My Lovely Team")
   .build(this as DslFactory)

new TeamFolderBuilder("My Lovely Team/My Lovely Service Group")
   .withDisplayName("My Lovely Service Group")
   .build(this as DslFactory)
```

Meanwhile `dsl_4489098a692c6e51ab4836f9b3bbc9cc_my_lovely_service.groovy` contains the definition for the pipeline and build/release jobs:

```groovy
import javaposse.jobdsl.dsl.DslFactory

import uk.gov.hmrc.buildjobs.domain.builder.PipelineJobBuilder
import uk.gov.hmrc.buildjobs.domain.builder.SbtMicroserviceJobBuilder

import static uk.gov.hmrc.buildjobs.domain.builder.pipeline.Environments.QA
import static uk.gov.hmrc.buildjobs.domain.builder.pipeline.Environments.STAGING

new PipelineJobBuilder("My Lovely Team/My Lovely Service Group", "my-lovely-service-pipeline")
   .buildMicroservice("my-lovely-service")
   .andThenDeployTo(QA)
   .andThenDeployTo(STAGING)
   .build(this as DslFactory)

new SbtMicroserviceJobBuilder("My Lovely Team/My Lovely Service Group", "my-lovely-service")
   .withMongo()
   .build(this as DslFactory)
```

## Limitations

* No tests
* Only supports a limit subset of jobs, and not all the various options on those
* Very rudimentary templating. We'd probably want something like [jinja2](https://github.com/pallets/jinja/)
* You have to copy the generated DSL to build-jobs yourself and raise a PR
* We don't handle some flows, like folder name changes or deleted jobs

## License

This code is open source software licensed under the [Apache 2.0 License]("http://www.apache.org/licenses/LICENSE-2.0.html").
