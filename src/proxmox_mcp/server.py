import sys

from mcp.server.fastmcp import FastMCP

from proxmox_mcp import backups, cloudinit, discovery, lifecycle, networking, permissions, snapshots, templates
from proxmox_mcp import storage as storage_mod
from proxmox_mcp.client import ProxmoxClient
from proxmox_mcp.config import Config

mcp = FastMCP("proxmox-mcp")

client: ProxmoxClient | None = None


@mcp.tool()
def proxmox_list_nodes() -> str:
    """List all nodes in the Proxmox cluster."""
    return discovery.list_nodes(client)


@mcp.tool()
def proxmox_node_status(node: str | None = None) -> str:
    """Get detailed status of a specific node."""
    return discovery.node_status(client, node)


@mcp.tool()
def proxmox_list_vms(node: str | None = None) -> str:
    """List all virtual machines in the cluster."""
    return discovery.list_vms(client, node)


@mcp.tool()
def proxmox_vm_info(
    node: str | None = None, vmid: int | None = None, name: str | None = None
) -> str:
    """Get detailed information about a specific VM."""
    return discovery.vm_info(client, node, vmid, name)


@mcp.tool()
def proxmox_list_lxc(node: str | None = None) -> str:
    """List all LXC containers in the cluster."""
    return discovery.list_lxc(client, node)


@mcp.tool()
def proxmox_lxc_info(
    node: str | None = None, vmid: int | None = None, name: str | None = None
) -> str:
    """Get detailed information about a specific LXC container."""
    return discovery.lxc_info(client, node, vmid, name)


@mcp.tool()
def proxmox_list_storage(node: str | None = None) -> str:
    """List all storage pools in the cluster."""
    return discovery.list_storage(client, node)


@mcp.tool()
def proxmox_storage_content(node: str | None = None, storage: str = "local") -> str:
    """List content in a storage pool."""
    return discovery.storage_content(client, node, storage)


@mcp.tool()
def proxmox_list_tasks(node: str | None = None, limit: int = 50) -> str:
    """List recent cluster tasks."""
    return discovery.list_tasks(client, node, limit)


@mcp.tool()
def proxmox_task_status(upid: str) -> str:
    """Get the status of a specific task."""
    return discovery.task_status(client, upid)


@mcp.tool()
def proxmox_node_metrics(
    node: str | None = None, timeframe: str = "hour", cf: str = "AVERAGE"
) -> str:
    """Get RRD metrics for a node."""
    return discovery.node_metrics(client, node, timeframe, cf)


@mcp.tool()
def proxmox_vm_metrics(
    node: str | None = None,
    vmid: int | None = None,
    name: str | None = None,
    timeframe: str = "hour",
) -> str:
    """Get RRD metrics for a VM."""
    return discovery.vm_metrics(client, node, vmid, name, timeframe)


@mcp.tool()
def proxmox_lxc_metrics(
    node: str | None = None,
    vmid: int | None = None,
    name: str | None = None,
    timeframe: str = "hour",
) -> str:
    """Get RRD metrics for an LXC container."""
    return discovery.lxc_metrics(client, node, vmid, name, timeframe)


@mcp.tool()
def proxmox_list_bridges(node: str | None = None) -> str:
    """List network bridges on a node."""
    return discovery.list_bridges(client, node)


@mcp.tool()
def proxmox_create_lxc(
    node: str | None = None,
    vmid: int | None = None,
    ostemplate: str = "",
    hostname: str | None = None,
    memory: int | None = None,
    cores: int | None = None,
    rootfs: str | None = None,
    password: str | None = None,
    start: bool = False,
    confirm: bool = False,
) -> str:
    """Create an LXC container (elevated, confirm required)."""
    return lifecycle.create_lxc(
        client, node=node, vmid=vmid, ostemplate=ostemplate,
        hostname=hostname, memory=memory, cores=cores,
        rootfs=rootfs, password=password, start=start, confirm=confirm,
    )


@mcp.tool()
def proxmox_start_lxc(
    node: str | None = None, vmid: int | None = None, confirm: bool = False
) -> str:
    """Start an LXC container (elevated, confirm required)."""
    return lifecycle.start_lxc(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_stop_lxc(
    node: str | None = None, vmid: int | None = None, confirm: bool = False
) -> str:
    """Stop an LXC container (elevated, confirm required)."""
    return lifecycle.stop_lxc(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_shutdown_lxc(
    node: str | None = None, vmid: int | None = None, confirm: bool = False
) -> str:
    """Shutdown an LXC container (elevated, confirm required)."""
    return lifecycle.shutdown_lxc(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_reboot_lxc(
    node: str | None = None, vmid: int | None = None, confirm: bool = False
) -> str:
    """Reboot an LXC container (elevated, confirm required)."""
    return lifecycle.reboot_lxc(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_delete_lxc(
    node: str | None = None, vmid: int | None = None, confirm: bool = False
) -> str:
    """Delete an LXC container (elevated, confirm required)."""
    return lifecycle.delete_lxc(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_configure_lxc(
    node: str | None = None,
    vmid: int | None = None,
    cores: int | None = None,
    memory: int | None = None,
    confirm: bool = False,
) -> str:
    """Configure an LXC container (elevated, confirm required)."""
    return lifecycle.configure_lxc(
        client, node=node, vmid=vmid, cores=cores, memory=memory, confirm=confirm,
    )


@mcp.tool()
def proxmox_create_vm(
    node: str | None = None,
    vmid: int | None = None,
    name: str | None = None,
    memory: int | None = None,
    cores: int | None = None,
    sockets: int | None = None,
    disk_size: str | None = None,
    storage: str | None = None,
    iso: str | None = None,
    ostype: str | None = None,
    net0: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a VM (elevated, confirm required)."""
    return lifecycle.create_vm(
        client, node=node, vmid=vmid, name=name, memory=memory, cores=cores,
        sockets=sockets, disk_size=disk_size, storage=storage, iso=iso,
        ostype=ostype, net0=net0, confirm=confirm,
    )


@mcp.tool()
def proxmox_start_vm(
    node: str | None = None, vmid: int | None = None, confirm: bool = False
) -> str:
    """Start a VM (elevated, confirm required)."""
    return lifecycle.start_vm(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_stop_vm(
    node: str | None = None, vmid: int | None = None, confirm: bool = False
) -> str:
    """Stop a VM (elevated, confirm required)."""
    return lifecycle.stop_vm(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_shutdown_vm(
    node: str | None = None, vmid: int | None = None, confirm: bool = False
) -> str:
    """Shutdown a VM (elevated, confirm required)."""
    return lifecycle.shutdown_vm(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_reboot_vm(
    node: str | None = None, vmid: int | None = None, confirm: bool = False
) -> str:
    """Reboot a VM (elevated, confirm required)."""
    return lifecycle.reboot_vm(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_delete_vm(
    node: str | None = None, vmid: int | None = None, confirm: bool = False
) -> str:
    """Delete a VM (elevated, confirm required)."""
    return lifecycle.delete_vm(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_clone_vm(
    node: str | None = None,
    vmid: int | None = None,
    newid: int | None = None,
    name: str | None = None,
    full: bool = True,
    confirm: bool = False,
) -> str:
    """Clone a VM (elevated, confirm required)."""
    return lifecycle.clone_vm(
        client, node=node, vmid=vmid, newid=newid, name=name, full=full, confirm=confirm,
    )


@mcp.tool()
def proxmox_migrate_vm(
    node: str | None = None,
    vmid: int | None = None,
    target: str | None = None,
    confirm: bool = False,
) -> str:
    """Migrate a VM to another node (elevated, confirm required)."""
    return lifecycle.migrate_vm(
        client, node=node, vmid=vmid, target=target, confirm=confirm,
    )


@mcp.tool()
def proxmox_configure_vm(
    node: str | None = None,
    vmid: int | None = None,
    cores: int | None = None,
    memory: int | None = None,
    confirm: bool = False,
) -> str:
    """Configure a VM (elevated, confirm required)."""
    return lifecycle.configure_vm(
        client, node=node, vmid=vmid, cores=cores, memory=memory, confirm=confirm,
    )


@mcp.tool()
def proxmox_list_templates(node: str | None = None) -> str:
    """List PVE appliance catalog (available templates to download)."""
    return templates.list_templates(client, node=node)


@mcp.tool()
def proxmox_list_storage_templates(node: str | None = None, storage: str = "local") -> str:
    """List already-downloaded templates in storage."""
    return templates.list_storage_templates(client, node=node, storage=storage)


@mcp.tool()
def proxmox_download_template(
    node: str | None = None,
    storage: str = "local",
    url: str = "",
    filename: str = "",
    confirm: bool = False,
) -> str:
    """Download template from PVE repo URL (elevated, confirm required)."""
    return templates.download_template(
        client, node=node, storage=storage, url=url, filename=filename, confirm=confirm,
    )


@mcp.tool()
def proxmox_upload_template(
    node: str | None = None,
    storage: str = "local",
    filepath: str = "",
    confirm: bool = False,
) -> str:
    """Upload local file as vztmpl to storage (elevated, confirm required)."""
    return templates.upload_template(
        client, node=node, storage=storage, filepath=filepath, confirm=confirm,
    )


@mcp.tool()
def proxmox_list_snapshots(
    node: str | None = None, vmid: int | None = None, vmtype: str = "qemu"
) -> str:
    """List snapshots for a VM or LXC container."""
    return snapshots.list_snapshots(client, node=node, vmid=vmid, vmtype=vmtype)


@mcp.tool()
def proxmox_create_snapshot(
    node: str | None = None,
    vmid: int | None = None,
    snapname: str = "",
    vmtype: str = "qemu",
    description: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a snapshot for a VM or LXC container (elevated, confirm required)."""
    return snapshots.create_snapshot(
        client, node=node, vmid=vmid, snapname=snapname,
        vmtype=vmtype, description=description, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_snapshot(
    node: str | None = None,
    vmid: int | None = None,
    snapname: str = "",
    vmtype: str = "qemu",
    confirm: bool = False,
) -> str:
    """Delete a snapshot for a VM or LXC container (elevated, confirm required)."""
    return snapshots.delete_snapshot(
        client, node=node, vmid=vmid, snapname=snapname,
        vmtype=vmtype, confirm=confirm,
    )


@mcp.tool()
def proxmox_rollback_snapshot(
    node: str | None = None,
    vmid: int | None = None,
    snapname: str = "",
    vmtype: str = "qemu",
    confirm: bool = False,
) -> str:
    """Rollback a snapshot for a VM or LXC container (elevated, confirm required)."""
    return snapshots.rollback_snapshot(
        client, node=node, vmid=vmid, snapname=snapname,
        vmtype=vmtype, confirm=confirm,
    )


@mcp.tool()
def proxmox_list_backups(node: str | None = None, storage: str = "local") -> str:
    """List backups in a storage pool."""
    return backups.list_backups(client, node=node, storage=storage)


@mcp.tool()
def proxmox_create_backup(
    node: str | None = None,
    vmid: int | None = None,
    vmtype: str = "qemu",
    storage: str = "local",
    mode: str = "snapshot",
    compress: str = "zstd",
    confirm: bool = False,
) -> str:
    """Create a backup for a VM or LXC container (elevated, confirm required)."""
    return backups.create_backup(
        client, node=node, vmid=vmid, vmtype=vmtype,
        storage=storage, mode=mode, compress=compress, confirm=confirm,
    )


@mcp.tool()
def proxmox_restore_backup(
    node: str | None = None,
    vmid: int | None = None,
    archive: str = "",
    storage: str = "local",
    vmtype: str = "qemu",
    confirm: bool = False,
) -> str:
    """Restore a backup (elevated, confirm required)."""
    return backups.restore_backup(
        client, node=node, vmid=vmid, archive=archive,
        storage=storage, vmtype=vmtype, confirm=confirm,
    )


@mcp.tool()
def proxmox_list_network(node: str | None = None) -> str:
    """List all network interfaces on a node."""
    return networking.list_network(client, node=node)


@mcp.tool()
def proxmox_create_network(
    node: str | None = None,
    iface: str = "",
    type: str = "bridge",
    address: str | None = None,
    netmask: str | None = None,
    gateway: str | None = None,
    bridge_ports: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a network interface on a node (elevated, confirm required)."""
    return networking.create_network(
        client, node=node, iface=iface, type=type,
        address=address, netmask=netmask, gateway=gateway,
        bridge_ports=bridge_ports, confirm=confirm,
    )


@mcp.tool()
def proxmox_update_network(
    node: str | None = None,
    iface: str = "",
    address: str | None = None,
    netmask: str | None = None,
    gateway: str | None = None,
    confirm: bool = False,
) -> str:
    """Update a network interface on a node (elevated, confirm required)."""
    return networking.update_network(
        client, node=node, iface=iface,
        address=address, netmask=netmask, gateway=gateway, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_network(
    node: str | None = None,
    iface: str = "",
    confirm: bool = False,
) -> str:
    """Delete a network interface on a node (elevated, confirm required)."""
    return networking.delete_network(
        client, node=node, iface=iface, confirm=confirm,
    )


@mcp.tool()
def proxmox_list_acl() -> str:
    """List ACL rules in the cluster."""
    return permissions.list_acl(client)


@mcp.tool()
def proxmox_set_acl(
    users: str = "",
    roles: str = "",
    path: str = "",
    propagate: bool = True,
    confirm: bool = False,
) -> str:
    """Set ACL rules (elevated, confirm required)."""
    return permissions.set_acl(
        client, users=users, roles=roles, path=path,
        propagate=propagate, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_acl(
    users: str = "",
    roles: str = "",
    path: str = "",
    propagate: bool = True,
    confirm: bool = False,
) -> str:
    """Delete ACL rules (elevated, confirm required)."""
    return permissions.delete_acl(
        client, users=users, roles=roles, path=path,
        propagate=propagate, confirm=confirm,
    )


@mcp.tool()
def proxmox_list_roles() -> str:
    """List roles in the cluster."""
    return permissions.list_roles(client)


@mcp.tool()
def proxmox_list_users() -> str:
    """List users in the cluster."""
    return permissions.list_users(client)


@mcp.tool()
def proxmox_list_tokens(userid: str = "") -> str:
    """List API tokens for a user."""
    return permissions.list_tokens(client, userid=userid)


@mcp.tool()
def proxmox_upload_iso(
    node: str | None = None,
    storage: str = "local",
    filepath: str = "",
    confirm: bool = False,
) -> str:
    """Upload an ISO file to storage (elevated, confirm required)."""
    return storage_mod.upload_iso(
        client, node=node, storage=storage, filepath=filepath, confirm=confirm,
    )


@mcp.tool()
def proxmox_list_isos(node: str | None = None, storage: str = "local") -> str:
    """List ISOs in a storage pool."""
    return storage_mod.list_isos(client, node=node, storage=storage)


@mcp.tool()
def proxmox_set_cloudinit(
    node: str | None = None,
    vmid: int | None = None,
    ciuser: str | None = None,
    cipassword: str | None = None,
    ipconfig0: str | None = None,
    sshkeys: str | None = None,
    confirm: bool = False,
) -> str:
    """Set cloud-init parameters on a VM (elevated, confirm required)."""
    return cloudinit.set_cloudinit(
        client, node=node, vmid=vmid, ciuser=ciuser,
        cipassword=cipassword, ipconfig0=ipconfig0,
        sshkeys=sshkeys, confirm=confirm,
    )


@mcp.tool()
def proxmox_exec_vm(
    node: str | None = None,
    vmid: int | None = None,
    command: str | None = None,
    confirm: bool = False,
) -> str:
    """Execute a command in a VM via QEMU Guest Agent (elevated, confirm required)."""
    return cloudinit.exec_vm(client, node=node, vmid=vmid, command=command, confirm=confirm)


@mcp.tool()
def proxmox_exec_lxc(
    node: str | None = None,
    vmid: int | None = None,
    command: str | None = None,
    confirm: bool = False,
) -> str:
    """Execute a command in an LXC container (elevated, confirm required)."""
    return cloudinit.exec_lxc(client, node=node, vmid=vmid, command=command, confirm=confirm)


def main() -> None:
    global client
    try:
        config = Config.from_env()
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    client = ProxmoxClient(config)

    mcp.run()


if __name__ == "__main__":
    main()
