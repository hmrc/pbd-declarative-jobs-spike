import hashlib

import yaml

def run_cli():
    service_name = "my-lovely-service" # This would be the repo name from the GitHub event
    with open(f"repository_yaml/{service_name}/repository.yaml", "r") as repository_yaml_file:
        repository_config = yaml.safe_load(repository_yaml_file)
    print(repository_config)
    build_folder = repository_config['build']['folder']
    folder_hash = hashlib.md5(build_folder.encode('utf-8')).hexdigest()
    folder_file_name = f"{folder_hash}.groovy"
    job_file_name = f"{folder_hash}-{service_name}.groovy"
    print(f"Please save the folder DSL to {folder_file_name}")
    print(f"Please save the job DSL to {job_file_name}")
    build_folders = build_folder.split('/')
    print(build_folders)
    folder_dsl = "import uk.gov.hmrc.buildjobs.domain.builder.TeamFolderBuilder\n\n"
    for depth in range(len(build_folders)):
        folder_dsl = folder_dsl + get_team_folder_builder(
            fully_qualified_folder_name="/".join(build_folders[0:depth+1]),
            folder_name=build_folders[depth],
        )
    with open(f"build/{folder_file_name}", "w") as folder_file:
        folder_file.write(folder_dsl)


def get_team_folder_builder(fully_qualified_folder_name: str, folder_name=str) -> str:
    return (
        f"new TeamFolderBuilder(\"{fully_qualified_folder_name}\")\n"
        f"   .withDisplayName(\"{folder_name}\")\n"
        "   .build(this as DslFactory)\n\n"
    )
