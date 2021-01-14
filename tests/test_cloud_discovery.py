def test_import_cloud_discovery():
    import cloud_discovery

    assert cloud_discovery is not None


def test_cloud_discovery_plugin_activation():
    from cloud_discovery.applications import CLOUD_DISCOVERY_APP
    from cloud_discovery.plugins import cloud_discovery_plugin

    my_app = CLOUD_DISCOVERY_APP()
    app = my_app.app
    app.plugins.activate(["cloud_discovery_plugin"])
    plugin = app.plugins.get("cloud_discovery_plugin")
    assert plugin is not None
    assert isinstance(plugin, cloud_discovery_plugin)


def test_cloud_discovery_plugin_azure_activation():
    from cloud_discovery.applications import CLOUD_DISCOVERY_APP
    from cloud_discovery.plugins import cloud_discovery_plugin_azure

    my_app = CLOUD_DISCOVERY_APP()
    app = my_app.app
    app.plugins.activate(["cloud_discovery_plugin_azure"])
    plugin = app.plugins.get("cloud_discovery_plugin_azure")
    assert plugin is not None
    assert isinstance(plugin, cloud_discovery_plugin_azure)


def test_cloud_discovery_plugin_do_activation():
    from cloud_discovery.applications import CLOUD_DISCOVERY_APP
    from cloud_discovery.plugins import cloud_discovery_plugin_do

    my_app = CLOUD_DISCOVERY_APP()
    app = my_app.app
    app.plugins.activate(["cloud_discovery_plugin_do"])
    plugin = app.plugins.get("cloud_discovery_plugin_do")
    assert plugin is not None
    assert isinstance(plugin, cloud_discovery_plugin_do)


def test_cloud_discovery_plugin_gce_activation():
    from cloud_discovery.applications import CLOUD_DISCOVERY_APP
    from cloud_discovery.plugins import cloud_discovery_plugin_gce

    my_app = CLOUD_DISCOVERY_APP()
    app = my_app.app
    app.plugins.activate(["cloud_discovery_plugin_gce"])
    plugin = app.plugins.get("cloud_discovery_plugin_gce")
    assert plugin is not None
    assert isinstance(plugin, cloud_discovery_plugin_gce)


def test_cloud_discovery_plugin_k8s_activation():
    from cloud_discovery.applications import CLOUD_DISCOVERY_APP
    from cloud_discovery.plugins import cloud_discovery_plugin_k8s

    my_app = CLOUD_DISCOVERY_APP()
    app = my_app.app
    app.plugins.activate(["cloud_discovery_plugin_k8s"])
    plugin = app.plugins.get("cloud_discovery_plugin_k8s")
    assert plugin is not None
    assert isinstance(plugin, cloud_discovery_plugin_k8s)


def test_cloud_discovery_plugin_li_activation():
    from cloud_discovery.applications import CLOUD_DISCOVERY_APP
    from cloud_discovery.plugins import cloud_discovery_plugin_linode

    my_app = CLOUD_DISCOVERY_APP()
    app = my_app.app
    app.plugins.activate(["cloud_discovery_plugin_linode"])
    plugin = app.plugins.get("cloud_discovery_plugin_linode")
    assert plugin is not None
    assert isinstance(plugin, cloud_discovery_plugin_linode)


def test_cloud_discovery_plugin_os_activation():
    from cloud_discovery.applications import CLOUD_DISCOVERY_APP
    from cloud_discovery.plugins import cloud_discovery_plugin_os

    my_app = CLOUD_DISCOVERY_APP()
    app = my_app.app
    app.plugins.activate(["cloud_discovery_plugin_os"])
    plugin = app.plugins.get("cloud_discovery_plugin_os")
    assert plugin is not None
    assert isinstance(plugin, cloud_discovery_plugin_os)
