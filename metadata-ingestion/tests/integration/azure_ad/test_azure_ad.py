import json
import pathlib
from unittest.mock import patch

from freezegun import freeze_time

from datahub.ingestion.run.pipeline import Pipeline
from datahub.ingestion.source.identity.azure_ad import AzureADConfig
from tests.test_helpers import mce_helpers

FROZEN_TIME = "2021-08-24 09:00:00"


def test_azure_ad_config():
    config = AzureADConfig.parse_obj(
        dict(
            client_id="00000000-0000-0000-0000-000000000000",
            tenant_id="00000000-0000-0000-0000-000000000000",
            client_secret="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            redirect="https://login.microsoftonline.com/common/oauth2/nativeclient",
            authority="https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000",
            token_url="https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000/oauth2/token",
            graph_url="https://graph.microsoft.com/v1.0",
            ingest_users=True,
            ingest_groups=True,
            ingest_group_membership=True,
        )
    )

    # Sanity on required configurations
    assert config.client_id == "00000000-0000-0000-0000-000000000000"
    assert config.tenant_id == "00000000-0000-0000-0000-000000000000"
    assert config.client_secret == "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    assert (
        config.redirect
        == "https://login.microsoftonline.com/common/oauth2/nativeclient"
    )
    assert (
        config.authority
        == "https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000"
    )
    assert (
        config.token_url
        == "https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000/oauth2/token"
    )
    assert config.graph_url == "https://graph.microsoft.com/v1.0"

    # assert on defaults
    assert config.ingest_users
    assert config.ingest_groups
    assert config.ingest_group_membership


@freeze_time(FROZEN_TIME)
def test_azure_ad_source_default_configs(pytestconfig, tmp_path):

    test_resources_dir: pathlib.Path = (
        pytestconfig.rootpath / "tests/integration/azure_ad"
    )

    with patch(
        "datahub.ingestion.source.identity.azure_ad.AzureADSource.get_token"
    ) as mock_token, patch(
        "datahub.ingestion.source.identity.azure_ad.AzureADSource._get_azure_ad_users"
    ) as mock_users, patch(
        "datahub.ingestion.source.identity.azure_ad.AzureADSource._get_azure_ad_groups"
    ) as mock_groups, patch(
        "datahub.ingestion.source.identity.azure_ad.AzureADSource._get_azure_ad_group_users"
    ) as mock_group_users:
        mocked_functions(
            test_resources_dir, mock_token, mock_users, mock_groups, mock_group_users
        )
        # Run an azure usage ingestion run.
        pipeline = Pipeline.create(
            {
                "run_id": "test-azure-ad",
                "source": {
                    "type": "azure-ad",
                    "config": {
                        "client_id": "00000000-0000-0000-0000-000000000000",
                        "tenant_id": "00000000-0000-0000-0000-000000000000",
                        "client_secret": "client_secret",
                        "redirect": "https://login.microsoftonline.com/common/oauth2/nativeclient",
                        "authority": "https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000",
                        "token_url": "https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000/oauth2/token",
                        "graph_url": "https://graph.microsoft.com/v1.0",
                        "ingest_group_membership": True,
                        "ingest_groups": True,
                        "ingest_users": True,
                    },
                },
                "sink": {
                    "type": "file",
                    "config": {
                        "filename": f"{tmp_path}/azure_ad_mces_default_config.json",
                    },
                },
            }
        )
        pipeline.run()
        pipeline.raise_from_status()

    mce_helpers.check_golden_file(
        pytestconfig,
        output_path=tmp_path / "azure_ad_mces_default_config.json",
        golden_path=test_resources_dir / "azure_ad_mces_golden_default_config.json",
    )


@freeze_time(FROZEN_TIME)
def test_azure_source_ingestion_disabled(pytestconfig, tmp_path):

    test_resources_dir: pathlib.Path = (
        pytestconfig.rootpath / "tests/integration/azure_ad"
    )

    with patch(
        "datahub.ingestion.source.identity.azure_ad.AzureADSource.get_token"
    ) as mock_token, patch(
        "datahub.ingestion.source.identity.azure_ad.AzureADSource._get_azure_ad_users"
    ) as mock_users, patch(
        "datahub.ingestion.source.identity.azure_ad.AzureADSource._get_azure_ad_groups"
    ) as mock_groups, patch(
        "datahub.ingestion.source.identity.azure_ad.AzureADSource._get_azure_ad_group_users"
    ) as mock_group_users:
        mocked_functions(
            test_resources_dir, mock_token, mock_users, mock_groups, mock_group_users
        )

        # Run an Azure usage ingestion run.
        pipeline = Pipeline.create(
            {
                "run_id": "test-azure-ad",
                "source": {
                    "type": "azure-ad",
                    "config": {
                        "client_id": "00000000-0000-0000-0000-000000000000",
                        "tenant_id": "00000000-0000-0000-0000-000000000000",
                        "client_secret": "client_secret",
                        "redirect": "https://login.microsoftonline.com/common/oauth2/nativeclient",
                        "authority": "https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000",
                        "token_url": "https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000/oauth2/token",
                        "graph_url": "https://graph.microsoft.com/v1.0",
                        "ingest_group_membership": "False",
                        "ingest_groups": "False",
                        "ingest_users": "False",
                    },
                },
                "sink": {
                    "type": "file",
                    "config": {
                        "filename": f"{tmp_path}/azure_ad_mces_ingestion_disabled.json",
                    },
                },
            }
        )
        pipeline.run()
        pipeline.raise_from_status()

    mce_helpers.check_golden_file(
        pytestconfig,
        output_path=tmp_path / "azure_ad_mces_ingestion_disabled.json",
        golden_path=test_resources_dir / "azure_ad_mces_golden_ingestion_disabled.json",
    )


def load_test_resources(test_resources_dir):
    azure_ad_users_json_file = test_resources_dir / "azure_ad_users.json"
    azure_ad_groups_json_file = test_resources_dir / "azure_ad_groups.json"

    with azure_ad_users_json_file.open() as azure_ad_users_json:
        reference_users = json.loads(azure_ad_users_json.read())

    with azure_ad_groups_json_file.open() as azure_ad_groups_json:
        reference_groups = json.loads(azure_ad_groups_json.read())

    return reference_users, reference_groups


def mocked_functions(
    test_resources_dir, mock_token, mock_users, mock_groups, mock_groups_users
):
    # mock token response
    mock_token.return_value = "xxxxxxxx"

    # mock users and groups response
    users, groups = load_test_resources(test_resources_dir)
    mock_users.return_value = iter(list([users]))
    mock_groups.return_value = iter(list([groups]))

    # For simplicity, each user is placed in ALL groups.
    # Create a separate response mock for each group in our sample data.
    r = []
    for _ in groups:
        r.append(users)
    mock_groups_users.return_value = iter(r)
