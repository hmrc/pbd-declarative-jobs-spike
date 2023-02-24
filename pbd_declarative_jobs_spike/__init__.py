import hashlib

from typing import List

import yaml

def run_cli():
    service_name = "my-lovely-service" # This would be the repo name from the GitHub event
    with open(f"repository_yaml/{service_name}/repository.yaml", "r") as repository_yaml_file:
        repository_config = yaml.safe_load(repository_yaml_file)
    build_folder = repository_config['namespace']
    folder_hash = hashlib.md5(build_folder.encode('utf-8')).hexdigest()
    folder_file_name = f"dsl_{folder_hash}.groovy"
    service_file_name = f"dsl_{folder_hash}_{service_name.replace('-', '_')}.groovy"
    build_folders = build_folder.split('/')
    folder_dsl = (
        "import javaposse.jobdsl.dsl.DslFactory\n\n"
        "import uk.gov.hmrc.buildjobs.domain.builder.TeamFolderBuilder\n\n"
    )
    for depth in range(len(build_folders)):
        folder_dsl = folder_dsl + get_team_folder_builder(
            fully_qualified_folder_name="/".join(build_folders[0:depth+1]),
            folder_name=build_folders[depth],
        )
    # We would really generate only the imports required
    service_dsl = (
        "import javaposse.jobdsl.dsl.DslFactory\n\n"
        "import uk.gov.hmrc.buildjobs.domain.builder.PipelineJobBuilder\n"
        "import uk.gov.hmrc.buildjobs.domain.builder.SbtMicroserviceJobBuilder\n"
        "import static uk.gov.hmrc.buildjobs.domain.builder.pipeline.Environments.INTEGRATION\n"
        "import static uk.gov.hmrc.buildjobs.domain.builder.pipeline.Environments.DEVELOPMENT\n"
        "import static uk.gov.hmrc.buildjobs.domain.builder.pipeline.Environments.QA\n"
        "import static uk.gov.hmrc.buildjobs.domain.builder.pipeline.Environments.STAGING\n\n"
    )
    service_dsl = service_dsl + get_pipeline_job_builder(
        fully_qualified_folder_name=build_folder,
        service_name=service_name,
        environments=repository_config["environments"]
    )
    service_dsl = service_dsl + get_sbt_micorservice_job_builder(
        fully_qualified_folder_name=build_folder,
        service_name=service_name,
        mongo=repository_config.get("mongo")
    )
    with open(f"build/{folder_file_name}", "w") as folder_file:
        folder_file.write(folder_dsl)
    with open(f"build/{service_file_name}", "w") as folder_file:
        folder_file.write(service_dsl)


def get_team_folder_builder(fully_qualified_folder_name: str, folder_name=str) -> str:
    return (
        f"new TeamFolderBuilder(\"{fully_qualified_folder_name}\")\n"
        f"   .withDisplayName(\"{folder_name}\")\n"
        f"   .build(this as DslFactory)\n\n"
    )


def get_pipeline_job_builder(fully_qualified_folder_name: str, service_name: str, environments: List[str]):
    dsl = (
        f"new PipelineJobBuilder(\"{fully_qualified_folder_name}\", \"{service_name}-pipeline\")\n"
        f"   .buildMicroservice(\"{service_name}\")\n"
    )
    for environment in environments:
        dsl = dsl + f"   .andThenDeployTo({environment.upper()})\n"
    dsl = dsl + f"   .build(this as DslFactory)\n\n"
    return dsl


def get_sbt_micorservice_job_builder(fully_qualified_folder_name: str, service_name: str, mongo: bool):
    dsl = f"new SbtMicroserviceJobBuilder(\"{fully_qualified_folder_name}\", \"{service_name}\")\n"
    if mongo:
        dsl = dsl + "   .withMongo()\n"
    dsl = dsl + "   .build(this as DslFactory)\n\n"
    return dsl

