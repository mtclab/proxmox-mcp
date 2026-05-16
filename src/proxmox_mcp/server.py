import sys

from mcp.server.fastmcp import FastMCP

from proxmox_mcp import (
    access,
    acme,
    apt,
    backups,
    capabilities,
    ceph,
    certificates,
    cloudinit,
    cluster,
    console,
    discovery,
    disks,
    firewall,
    ha,
    hardware,
    lifecycle,
    mapping,
    metrics,
    networking,
    nodes,
    notifications,
    permissions,
    pools,
    replication,
    sdn,
    snapshots,
    tasks,
    templates,
)
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
def proxmox_resize_lxc(
    node: str | None = None,
    vmid: int | None = None,
    disk: str = "rootfs",
    size: str = "+10G",
    confirm: bool = False,
) -> str:
    """Resize an LXC container disk (elevated, confirm required)."""
    return lifecycle.resize_lxc(
        client, node=node, vmid=vmid, disk=disk, size=size, confirm=confirm,
    )


@mcp.tool()
def proxmox_suspend_lxc(
    node: str | None = None, vmid: int | None = None, confirm: bool = False
) -> str:
    """Suspend an LXC container (elevated, confirm required)."""
    return lifecycle.suspend_lxc(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_resume_lxc(
    node: str | None = None, vmid: int | None = None, confirm: bool = False
) -> str:
    """Resume a suspended LXC container (elevated, confirm required)."""
    return lifecycle.resume_lxc(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_clone_lxc(
    node: str | None = None,
    vmid: int | None = None,
    newid: int | None = None,
    hostname: str | None = None,
    full: bool = True,
    target: str | None = None,
    confirm: bool = False,
) -> str:
    """Clone an LXC container (elevated, confirm required)."""
    return lifecycle.clone_lxc(
        client, node=node, vmid=vmid, newid=newid,
        hostname=hostname, full=full, target=target, confirm=confirm,
    )


@mcp.tool()
def proxmox_migrate_lxc(
    node: str | None = None,
    vmid: int | None = None,
    target: str | None = None,
    confirm: bool = False,
) -> str:
    """Migrate an LXC container to another node (elevated, confirm required)."""
    return lifecycle.migrate_lxc(
        client, node=node, vmid=vmid, target=target, confirm=confirm,
    )


@mcp.tool()
def proxmox_lxc_interfaces(
    node: str | None = None, vmid: int | None = None
) -> str:
    """Get network interfaces and IP addresses for an LXC container."""
    return lifecycle.lxc_interfaces(client, node=node, vmid=vmid)


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
    """Create a VM (elevated, confirm required). disk_size uses scsi0 format."""
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
def proxmox_resize_vm(
    node: str | None = None,
    vmid: int | None = None,
    disk: str = "scsi0",
    size: str = "+10G",
    confirm: bool = False,
) -> str:
    """Resize a VM disk (elevated, confirm required)."""
    return lifecycle.resize_vm(
        client, node=node, vmid=vmid, disk=disk, size=size, confirm=confirm,
    )


@mcp.tool()
def proxmox_reset_vm(
    node: str | None = None, vmid: int | None = None, confirm: bool = False
) -> str:
    """Reset a VM (hardware reset, elevated, confirm required)."""
    return lifecycle.reset_vm(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_suspend_vm(
    node: str | None = None, vmid: int | None = None, confirm: bool = False
) -> str:
    """Suspend a VM (elevated, confirm required)."""
    return lifecycle.suspend_vm(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_resume_vm(
    node: str | None = None, vmid: int | None = None, confirm: bool = False
) -> str:
    """Resume a suspended VM (elevated, confirm required)."""
    return lifecycle.resume_vm(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_snapshot_config(
    node: str | None = None,
    vmid: int | None = None,
    snapname: str = "",
    vmtype: str = "qemu",
) -> str:
    """Get snapshot configuration (read-only)."""
    return snapshots.snapshot_config(
        client, node=node, vmid=vmid, snapname=snapname, vmtype=vmtype,
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
    """Create a backup (elevated, confirm required). vmtype: 'qemu' or 'lxc'."""
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
    apply: bool = False,
) -> str:
    """Create a network interface on a node (elevated, confirm required)."""
    return networking.create_network(
        client, node=node, iface=iface, type=type,
        address=address, netmask=netmask, gateway=gateway,
        bridge_ports=bridge_ports, confirm=confirm, apply=apply,
    )


@mcp.tool()
def proxmox_update_network(
    node: str | None = None,
    iface: str = "",
    address: str | None = None,
    netmask: str | None = None,
    gateway: str | None = None,
    confirm: bool = False,
    apply: bool = False,
) -> str:
    """Update a network interface on a node (elevated, confirm required)."""
    return networking.update_network(
        client, node=node, iface=iface,
        address=address, netmask=netmask, gateway=gateway, confirm=confirm,
        apply=apply,
    )


@mcp.tool()
def proxmox_delete_network(
    node: str | None = None,
    iface: str = "",
    confirm: bool = False,
    apply: bool = False,
) -> str:
    """Delete a network interface on a node (elevated, confirm required)."""
    return networking.delete_network(
        client, node=node, iface=iface, confirm=confirm, apply=apply,
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
def proxmox_create_user(
    userid: str = "",
    password: str = "",
    comment: str | None = None,
    email: str | None = None,
    firstname: str | None = None,
    lastname: str | None = None,
    enable: bool | None = None,
    expire: int | None = None,
    groups: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a new PVE user (elevated, confirm required)."""
    return permissions.create_user(
        client, userid=userid, password=password, comment=comment,
        email=email, firstname=firstname, lastname=lastname,
        enable=enable, expire=expire, groups=groups, confirm=confirm,
    )


@mcp.tool()
def proxmox_get_user(userid: str = "") -> str:
    """Get PVE user configuration (read-only)."""
    return permissions.get_user(client, userid=userid)


@mcp.tool()
def proxmox_update_user(
    userid: str = "",
    comment: str | None = None,
    email: str | None = None,
    firstname: str | None = None,
    lastname: str | None = None,
    enable: bool | None = None,
    expire: int | None = None,
    groups: str | None = None,
    confirm: bool = False,
) -> str:
    """Update a PVE user (elevated, confirm required)."""
    return permissions.update_user(
        client, userid=userid, comment=comment, email=email,
        firstname=firstname, lastname=lastname, enable=enable,
        expire=expire, groups=groups, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_user(
    userid: str = "",
    confirm: bool = False,
) -> str:
    """Delete a PVE user (elevated, confirm required)."""
    return permissions.delete_user(client, userid=userid, confirm=confirm)


@mcp.tool()
def proxmox_create_role(
    roleid: str = "",
    privs: str = "",
    confirm: bool = False,
) -> str:
    """Create a new PVE role (elevated, confirm required)."""
    return permissions.create_role(client, roleid=roleid, privs=privs, confirm=confirm)


@mcp.tool()
def proxmox_get_role(roleid: str = "") -> str:
    """Get PVE role configuration (read-only)."""
    return permissions.get_role(client, roleid=roleid)


@mcp.tool()
def proxmox_update_role(
    roleid: str = "",
    privs: str = "",
    confirm: bool = False,
) -> str:
    """Update a PVE role (elevated, confirm required)."""
    return permissions.update_role(client, roleid=roleid, privs=privs, confirm=confirm)


@mcp.tool()
def proxmox_delete_role(
    roleid: str = "",
    confirm: bool = False,
) -> str:
    """Delete a PVE role (elevated, confirm required)."""
    return permissions.delete_role(client, roleid=roleid, confirm=confirm)


@mcp.tool()
def proxmox_create_token(
    userid: str = "",
    tokenid: str = "",
    comment: str | None = None,
    privsep: bool | None = None,
    expire: int | None = None,
    confirm: bool = False,
) -> str:
    """Create an API token for a PVE user (elevated, confirm required)."""
    return permissions.create_token(
        client, userid=userid, tokenid=tokenid, comment=comment,
        privsep=privsep, expire=expire, confirm=confirm,
    )


@mcp.tool()
def proxmox_get_token(userid: str = "", tokenid: str = "") -> str:
    """Get API token info (read-only)."""
    return permissions.get_token(client, userid=userid, tokenid=tokenid)


@mcp.tool()
def proxmox_update_token(
    userid: str = "",
    tokenid: str = "",
    comment: str | None = None,
    privsep: bool | None = None,
    expire: int | None = None,
    confirm: bool = False,
) -> str:
    """Update an API token (elevated, confirm required)."""
    return permissions.update_token(
        client, userid=userid, tokenid=tokenid, comment=comment,
        privsep=privsep, expire=expire, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_token(
    userid: str = "",
    tokenid: str = "",
    confirm: bool = False,
) -> str:
    """Delete an API token (elevated, confirm required)."""
    return permissions.delete_token(client, userid=userid, tokenid=tokenid, confirm=confirm)


@mcp.tool()
def proxmox_list_groups() -> str:
    """List PVE groups (read-only)."""
    return permissions.list_groups(client)


@mcp.tool()
def proxmox_create_group(
    groupid: str = "",
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a PVE group (elevated, confirm required)."""
    return permissions.create_group(client, groupid=groupid, comment=comment, confirm=confirm)


@mcp.tool()
def proxmox_get_group(groupid: str = "") -> str:
    """Get PVE group configuration (read-only)."""
    return permissions.get_group(client, groupid=groupid)


@mcp.tool()
def proxmox_update_group(
    groupid: str = "",
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Update a PVE group (elevated, confirm required)."""
    return permissions.update_group(client, groupid=groupid, comment=comment, confirm=confirm)


@mcp.tool()
def proxmox_delete_group(
    groupid: str = "",
    confirm: bool = False,
) -> str:
    """Delete a PVE group (elevated, confirm required)."""
    return permissions.delete_group(client, groupid=groupid, confirm=confirm)


@mcp.tool()
def proxmox_check_permissions(
    userid: str | None = None,
    path: str | None = None,
) -> str:
    """Check effective permissions for a user/path (read-only)."""
    return permissions.check_permissions(client, userid=userid, path=path)


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
@mcp.tool()
def proxmox_node_config(node: str | None = None) -> str:
    """Get node configuration (read-only)."""
    return nodes.node_config(client, node=node)


@mcp.tool()
def proxmox_update_node_config(
    node: str | None = None,
    description: str | None = None,
    keyboard: str | None = None,
    time_zone: str | None = None,
    confirm: bool = False,
) -> str:
    """Update node configuration (elevated, confirm required)."""
    return nodes.update_node_config(
        client, node=node, description=description,
        keyboard=keyboard, time_zone=time_zone, confirm=confirm,
    )


@mcp.tool()
def proxmox_reboot_node(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Reboot a node (elevated, confirm required)."""
    return nodes.reboot_node(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_shutdown_node(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Shutdown a node (elevated, confirm required)."""
    return nodes.shutdown_node(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_start_all(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Start all VMs/containers on a node (elevated, confirm required)."""
    return nodes.start_all(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_stop_all(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Stop all VMs/containers on a node (elevated, confirm required)."""
    return nodes.stop_all(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_suspend_all(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Suspend all VMs on a node (elevated, confirm required)."""
    return nodes.suspend_all(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_migrate_all(
    node: str | None = None,
    target: str | None = None,
    confirm: bool = False,
) -> str:
    """Migrate all VMs/containers on a node (elevated, confirm required)."""
    return nodes.migrate_all(client, node=node, target=target, confirm=confirm)


@mcp.tool()
def proxmox_get_node_detailed_status(node: str | None = None) -> str:
    """Get detailed node status (read-only)."""
    return nodes.get_node_detailed_status(client, node=node)


@mcp.tool()
def proxmox_list_services(node: str | None = None) -> str:
    """List services on a node."""
    return nodes.list_services(client, node=node)


@mcp.tool()
def proxmox_service_state(
    node: str | None = None,
    service: str = "",
) -> str:
    """Get service state on a node."""
    return nodes.service_state(client, node=node, service=service)


@mcp.tool()
def proxmox_start_service(
    node: str | None = None,
    service: str = "",
    confirm: bool = False,
) -> str:
    """Start a service on a node (elevated, confirm required)."""
    return nodes.start_service(client, node=node, service=service, confirm=confirm)


@mcp.tool()
def proxmox_stop_service(
    node: str | None = None,
    service: str = "",
    confirm: bool = False,
) -> str:
    """Stop a service on a node (elevated, confirm required)."""
    return nodes.stop_service(client, node=node, service=service, confirm=confirm)


@mcp.tool()
def proxmox_restart_service(
    node: str | None = None,
    service: str = "",
    confirm: bool = False,
) -> str:
    """Restart a service on a node (elevated, confirm required)."""
    return nodes.restart_service(client, node=node, service=service, confirm=confirm)


@mcp.tool()
def proxmox_node_dns(node: str | None = None) -> str:
    """Get DNS settings for a node."""
    return nodes.node_dns(client, node=node)


@mcp.tool()
def proxmox_node_hosts(node: str | None = None) -> str:
    """Get hosts file content for a node."""
    return nodes.node_hosts(client, node=node)


@mcp.tool()
def proxmox_exec_vm(
    node: str | None = None,
    vmid: int | None = None,
    command: str | None = None,
    confirm: bool = False,
) -> str:
    """Execute a command in a VM via QEMU Guest Agent (elevated, confirm required).
    Commands restricted by PROXMOX_ALLOWED_COMMANDS allowlist if configured."""
    return cloudinit.exec_vm(client, node=node, vmid=vmid, command=command, confirm=confirm)


@mcp.tool()
def proxmox_agent_ping(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = True,
) -> str:
    """Ping QEMU Guest Agent on a VM (elevated, confirm required)."""
    return cloudinit.agent_ping(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_agent_info(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get QEMU Guest Agent info for a VM (elevated, read-only)."""
    return cloudinit.agent_info(client, node=node, vmid=vmid)


@mcp.tool()
def proxmox_agent_network_interfaces(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get network interfaces from QEMU Guest Agent (elevated, read-only)."""
    return cloudinit.agent_network_interfaces(client, node=node, vmid=vmid)


@mcp.tool()
def proxmox_agent_osinfo(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get OS info from QEMU Guest Agent (elevated, read-only)."""
    return cloudinit.agent_osinfo(client, node=node, vmid=vmid)


@mcp.tool()
def proxmox_agent_fsinfo(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get filesystem info from QEMU Guest Agent (elevated, read-only)."""
    return cloudinit.agent_fsinfo(client, node=node, vmid=vmid)


@mcp.tool()
def proxmox_agent_exec_status(
    node: str | None = None,
    vmid: int | None = None,
    pid: int | None = None,
) -> str:
    """Get exec status of a command started via QEMU Guest Agent (elevated, read-only)."""
    return cloudinit.agent_exec_status(client, node=node, vmid=vmid, pid=pid)


@mcp.tool()
def proxmox_agent_fsfreeze(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = True,
) -> str:
    """Freeze filesystems on a VM via QEMU Guest Agent (elevated, confirm required)."""
    return cloudinit.agent_fsfreeze(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_agent_fsthaw(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = True,
) -> str:
    """Thaw filesystems on a VM via QEMU Guest Agent (elevated, confirm required)."""
    return cloudinit.agent_fsthaw(client, node=node, vmid=vmid, confirm=confirm)

@mcp.tool()
def proxmox_agent_fstrim(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = True,
) -> str:
    """Run fstrim on VM filesystem via QEMU Guest Agent (elevated, confirm required)."""
    return cloudinit.agent_fstrim(client, node=node, vmid=vmid, confirm=confirm)

@mcp.tool()
def proxmox_agent_fsfreeze_status(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Check filesystem freeze status via QEMU Guest Agent (elevated)."""
    return cloudinit.agent_fsfreeze_status(client, node=node, vmid=vmid)

@mcp.tool()
def proxmox_agent_get_host_name(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get VM hostname via QEMU Guest Agent (elevated)."""
    return cloudinit.agent_get_host_name(client, node=node, vmid=vmid)

@mcp.tool()
def proxmox_agent_get_memory_block_info(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get VM memory block info via QEMU Guest Agent (elevated)."""
    return cloudinit.agent_get_memory_block_info(client, node=node, vmid=vmid)

@mcp.tool()
def proxmox_agent_get_memory_blocks(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get VM memory blocks via QEMU Guest Agent (elevated)."""
    return cloudinit.agent_get_memory_blocks(client, node=node, vmid=vmid)

@mcp.tool()
def proxmox_agent_get_time(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get VM time via QEMU Guest Agent (elevated)."""
    return cloudinit.agent_get_time(client, node=node, vmid=vmid)

@mcp.tool()
def proxmox_agent_get_timezone(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get VM timezone via QEMU Guest Agent (elevated)."""
    return cloudinit.agent_get_timezone(client, node=node, vmid=vmid)

@mcp.tool()
def proxmox_agent_get_users(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get VM users via QEMU Guest Agent (elevated)."""
    return cloudinit.agent_get_users(client, node=node, vmid=vmid)

@mcp.tool()
def proxmox_agent_get_vcpus(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get VM VCPU info via QEMU Guest Agent (elevated)."""
    return cloudinit.agent_get_vcpus(client, node=node, vmid=vmid)

@mcp.tool()
def proxmox_agent_set_user_password(
    node: str | None = None,
    vmid: int | None = None,
    username: str = "",
    password: str = "",
    confirm: bool = True,
) -> str:
    """Set user password in VM via QEMU Guest Agent (elevated, confirm required)."""
    return cloudinit.agent_set_user_password(
        client, node=node, vmid=vmid, username=username, password=password, confirm=confirm,
    )

@mcp.tool()
def proxmox_agent_file_read(
    node: str | None = None,
    vmid: int | None = None,
    filepath: str = "",
) -> str:
    """Read a file from VM via QEMU Guest Agent (elevated)."""
    return cloudinit.agent_file_read(client, node=node, vmid=vmid, filepath=filepath)

@mcp.tool()
def proxmox_agent_file_write(
    node: str | None = None,
    vmid: int | None = None,
    filepath: str = "",
    content: str = "",
    confirm: bool = True,
) -> str:
    """Write a file to VM via QEMU Guest Agent (elevated, confirm required)."""
    return cloudinit.agent_file_write(client, node=node, vmid=vmid, filepath=filepath, content=content, confirm=confirm)

@mcp.tool()
def proxmox_agent_shutdown(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = True,
) -> str:
    """Shutdown VM via QEMU Guest Agent (elevated, confirm required)."""
    return cloudinit.agent_shutdown(client, node=node, vmid=vmid, confirm=confirm)

@mcp.tool()
def proxmox_agent_suspend_disk(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = True,
) -> str:
    """Suspend VM to disk via QEMU Guest Agent (elevated, confirm required)."""
    return cloudinit.agent_suspend_disk(client, node=node, vmid=vmid, confirm=confirm)

@mcp.tool()
def proxmox_agent_suspend_ram(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = True,
) -> str:
    """Suspend VM to RAM via QEMU Guest Agent (elevated, confirm required)."""
    return cloudinit.agent_suspend_ram(client, node=node, vmid=vmid, confirm=confirm)

@mcp.tool()
def proxmox_agent_suspend_hybrid(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = True,
) -> str:
    """Hybrid suspend VM via QEMU Guest Agent (elevated, confirm required)."""
    return cloudinit.agent_suspend_hybrid(client, node=node, vmid=vmid, confirm=confirm)

@mcp.tool()
def proxmox_get_storage(storage: str, node: str | None = None) -> str:
    """Get detailed storage configuration (read-only)."""
    return storage_mod.get_storage(client, storage=storage, node=node)


@mcp.tool()
def proxmox_create_storage(
    storage: str,
    type: str = "dir",
    path: str | None = None,
    content: str | None = None,
    nodes: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a storage pool (elevated, confirm required)."""
    return storage_mod.create_storage(
        client, storage=storage, type=type, path=path,
        content=content, nodes=nodes, confirm=confirm,
    )


@mcp.tool()
def proxmox_update_storage(
    storage: str,
    content: str | None = None,
    nodes: str | None = None,
    delete: str | None = None,
    confirm: bool = False,
) -> str:
    """Update a storage pool configuration (elevated, confirm required)."""
    return storage_mod.update_storage(
        client, storage=storage, content=content,
        nodes=nodes, delete=delete, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_storage(
    storage: str,
    confirm: bool = False,
) -> str:
    """Delete a storage pool (elevated, confirm required)."""
    return storage_mod.delete_storage(client, storage=storage, confirm=confirm)


@mcp.tool()
def proxmox_delete_volume(
    node: str | None = None,
    storage: str = "local",
    volume: str = "",
    confirm: bool = False,
) -> str:
    """Delete a volume from storage (elevated, confirm required)."""
    return storage_mod.delete_volume(
        client, node=node, storage=storage, volume=volume, confirm=confirm,
    )


@mcp.tool()
def proxmox_prune_backups(
    node: str | None = None,
    storage: str = "local",
    prune_type: str | None = None,
    confirm: bool = False,
) -> str:
    """Prune backups on storage (elevated, confirm required)."""
    return storage_mod.prune_backups(
        client, node=node, storage=storage, prune_type=prune_type, confirm=confirm,
    )


@mcp.tool()
def proxmox_storage_status(
    node: str | None = None,
    storage: str = "local",
) -> str:
    """Get storage status on a node (read-only)."""
    return storage_mod.storage_status(client, node=node, storage=storage)


@mcp.tool()
def proxmox_cluster_options() -> str:
    """Get datacenter options (read-only)."""
    return cluster.cluster_options(client)


@mcp.tool()
def proxmox_update_cluster_options(confirm: bool = False, **kwargs: str) -> str:
    """Update datacenter options (elevated, confirm required)."""
    return cluster.update_cluster_options(client, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_list_backup_jobs() -> str:
    """List scheduled backup jobs (read-only)."""
    return cluster.list_backup_jobs(client)


@mcp.tool()
def proxmox_create_backup_job(
    id: str = "",
    schedule: str | None = None,
    vmid: str | None = None,
    storage: str | None = None,
    mode: str | None = None,
    compress: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a backup job (elevated, confirm required)."""
    return cluster.create_backup_job(
        client, id=id, schedule=schedule, vmid=vmid,
        storage=storage, mode=mode, compress=compress, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_backup_job(
    id: str = "",
    confirm: bool = False,
) -> str:
    """Delete a backup job (elevated, confirm required)."""
    return cluster.delete_backup_job(client, id=id, confirm=confirm)


@mcp.tool()
def proxmox_move_vm_disk(
    node: str | None = None,
    vmid: int | None = None,
    disk: str = "scsi0",
    storage: str | None = None,
    format: str | None = None,
    confirm: bool = False,
) -> str:
    """Move a VM disk to different storage (elevated, confirm required)."""
    return lifecycle.move_vm_disk(
        client, node=node, vmid=vmid, disk=disk, storage=storage, format=format, confirm=confirm,
    )


@mcp.tool()
def proxmox_convert_to_template(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = False,
) -> str:
    """Convert a VM to template (destructive, elevated, confirm required)."""
    return lifecycle.convert_to_template(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_convert_lxc_to_template(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = False,
) -> str:
    """Convert an LXC container to template (destructive, elevated, confirm required)."""
    return lifecycle.convert_lxc_to_template(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_lxc_feature_check(
    node: str | None = None,
    vmid: int | None = None,
    feature: str = "",
) -> str:
    """Check if a feature is available for an LXC container (read-only)."""
    return lifecycle.lxc_feature_check(client, node=node, vmid=vmid, feature=feature)


@mcp.tool()
def proxmox_vm_feature_check(
    node: str | None = None,
    vmid: int | None = None,
    feature: str = "",
) -> str:
    """Check if a feature is available for a VM (read-only)."""
    return lifecycle.vm_feature_check(client, node=node, vmid=vmid, feature=feature)


@mcp.tool()
def proxmox_vm_pending_config(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get pending configuration changes for a VM (read-only)."""
    return lifecycle.vm_pending_config(client, node=node, vmid=vmid)


@mcp.tool()
def proxmox_lxc_pending_config(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get pending configuration changes for an LXC container (read-only)."""
    return lifecycle.lxc_pending_config(client, node=node, vmid=vmid)


@mcp.tool()
def proxmox_list_pools() -> str:
    """List all pools (read-only)."""
    return pools.list_pools(client)


@mcp.tool()
def proxmox_get_pool(poolid: str) -> str:
    """Get details of a pool (read-only)."""
    return pools.get_pool(client, poolid=poolid)


@mcp.tool()
def proxmox_create_pool(
    poolid: str = "",
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a pool (elevated, confirm required)."""
    return pools.create_pool(client, poolid=poolid, comment=comment, confirm=confirm)


@mcp.tool()
def proxmox_update_pool(
    poolid: str = "",
    comment: str | None = None,
    delete: str | None = None,
    members: str | None = None,
    confirm: bool = False,
) -> str:
    """Update a pool (elevated, confirm required)."""
    return pools.update_pool(
        client, poolid=poolid, comment=comment, delete=delete, members=members, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_pool(
    poolid: str = "",
    confirm: bool = False,
) -> str:
    """Delete a pool (elevated, confirm required)."""
    return pools.delete_pool(client, poolid=poolid, confirm=confirm)


@mcp.tool()
def proxmox_task_log(
    upid: str,
    node: str | None = None,
    limit: int | None = None,
) -> str:
    """Get task log entries (read-only)."""
    return tasks.task_log(client, upid=upid, node=node, limit=limit)


@mcp.tool()
def proxmox_cluster_status() -> str:
    """Get cluster quorum and health status (read-only)."""
    return discovery.cluster_status(client)


@mcp.tool()
def proxmox_ceph_status() -> str:
    """Get Ceph cluster status (read-only)."""
    return ceph.ceph_status(client)


@mcp.tool()
def proxmox_ceph_metadata() -> str:
    """Get Ceph cluster metadata (read-only)."""
    return ceph.ceph_metadata(client)


@mcp.tool()
def proxmox_node_ceph_status(node: str | None = None) -> str:
    """Get Ceph status for a specific node (read-only)."""
    return ceph.node_ceph_status(client, node=node)


@mcp.tool()
def proxmox_cluster_resources(type: str | None = None) -> str:
    """List all cluster resources, optionally filtered by type (vm, storage, node, sdn)."""
    return discovery.cluster_resources(client, type=type)


@mcp.tool()
def proxmox_list_cluster_firewall_rules() -> str:
    """List cluster-level firewall rules."""
    return firewall.list_cluster_firewall_rules(client)


@mcp.tool()
def proxmox_create_cluster_firewall_rule(
    action: str = "ACCEPT",
    dptype: str | None = None,
    dport: str | None = None,
    sport: str | None = None,
    proto: str | None = None,
    source: str | None = None,
    dest: str | None = None,
    iface: str | None = None,
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a cluster firewall rule (elevated, confirm required)."""
    return firewall.create_cluster_firewall_rule(
        client, action=action, dptype=dptype, dport=dport,
        sport=sport, proto=proto, source=source, dest=dest,
        iface=iface, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_get_cluster_firewall_rule(pos: int = 0) -> str:
    """Get a specific cluster firewall rule by position."""
    return firewall.get_cluster_firewall_rule(client, pos=pos)


@mcp.tool()
def proxmox_update_cluster_firewall_rule(
    pos: int = 0,
    action: str | None = None,
    dptype: str | None = None,
    dport: str | None = None,
    sport: str | None = None,
    proto: str | None = None,
    source: str | None = None,
    dest: str | None = None,
    iface: str | None = None,
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Update a cluster firewall rule (elevated, confirm required)."""
    return firewall.update_cluster_firewall_rule(
        client, pos=pos, action=action, dptype=dptype, dport=dport,
        sport=sport, proto=proto, source=source, dest=dest,
        iface=iface, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_cluster_firewall_rule(
    pos: int = 0,
    confirm: bool = False,
) -> str:
    """Delete a cluster firewall rule (elevated, confirm required)."""
    return firewall.delete_cluster_firewall_rule(client, pos=pos, confirm=confirm)


@mcp.tool()
def proxmox_get_cluster_firewall_options() -> str:
    """Get cluster firewall options (read-only)."""
    return firewall.get_cluster_firewall_options(client)


@mcp.tool()
def proxmox_set_cluster_firewall_options(confirm: bool = False, **kwargs: str) -> str:
    """Set cluster firewall options (elevated, confirm required)."""
    return firewall.set_cluster_firewall_options(client, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_list_cluster_firewall_aliases() -> str:
    """List cluster firewall aliases."""
    return firewall.list_cluster_firewall_aliases(client)


@mcp.tool()
def proxmox_create_cluster_firewall_alias(
    name: str = "",
    cidr: str = "",
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a cluster firewall alias (elevated, confirm required)."""
    return firewall.create_cluster_firewall_alias(
        client, name=name, cidr=cidr, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_cluster_firewall_alias(
    name: str = "",
    confirm: bool = False,
) -> str:
    """Delete a cluster firewall alias (elevated, confirm required)."""
    return firewall.delete_cluster_firewall_alias(client, name=name, confirm=confirm)


@mcp.tool()
def proxmox_list_cluster_firewall_ipsets() -> str:
    """List cluster firewall IPSets."""
    return firewall.list_cluster_firewall_ipsets(client)


@mcp.tool()
def proxmox_list_cluster_firewall_refs() -> str:
    """List cluster firewall references (IPSet/Alias)."""
    return firewall.list_cluster_firewall_refs(client)


@mcp.tool()
def proxmox_list_node_firewall_rules(node: str | None = None) -> str:
    """List node-level firewall rules."""
    return firewall.list_node_firewall_rules(client, node=node)


@mcp.tool()
def proxmox_create_node_firewall_rule(
    node: str | None = None,
    action: str = "ACCEPT",
    dptype: str | None = None,
    dport: str | None = None,
    sport: str | None = None,
    proto: str | None = None,
    source: str | None = None,
    dest: str | None = None,
    iface: str | None = None,
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a node firewall rule (elevated, confirm required)."""
    return firewall.create_node_firewall_rule(
        client, node=node, action=action, dptype=dptype, dport=dport,
        sport=sport, proto=proto, source=source, dest=dest,
        iface=iface, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_node_firewall_rule(
    node: str | None = None,
    pos: int = 0,
    confirm: bool = False,
) -> str:
    """Delete a node firewall rule (elevated, confirm required)."""
    return firewall.delete_node_firewall_rule(client, node=node, pos=pos, confirm=confirm)


@mcp.tool()
def proxmox_get_node_firewall_options(node: str | None = None) -> str:
    """Get node firewall options (read-only)."""
    return firewall.get_node_firewall_options(client, node=node)


@mcp.tool()
def proxmox_list_vm_firewall_rules(
    node: str | None = None,
    vmid: int | None = None,
    vmtype: str = "qemu",
) -> str:
    """List VM-level firewall rules. vmtype: 'qemu' or 'lxc'."""
    return firewall.list_vm_firewall_rules(client, node=node, vmid=vmid, vmtype=vmtype)


@mcp.tool()
def proxmox_create_vm_firewall_rule(
    node: str | None = None,
    vmid: int | None = None,
    vmtype: str = "qemu",
    action: str = "ACCEPT",
    dptype: str | None = None,
    dport: str | None = None,
    sport: str | None = None,
    proto: str | None = None,
    source: str | None = None,
    dest: str | None = None,
    iface: str | None = None,
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a VM firewall rule (elevated, confirm required). vmtype: 'qemu' or 'lxc'."""
    return firewall.create_vm_firewall_rule(
        client, node=node, vmid=vmid, vmtype=vmtype, action=action,
        dptype=dptype, dport=dport, sport=sport, proto=proto,
        source=source, dest=dest, iface=iface, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_vm_firewall_rule(
    node: str | None = None,
    vmid: int | None = None,
    pos: int = 0,
    vmtype: str = "qemu",
    confirm: bool = False,
) -> str:
    """Delete a VM firewall rule (elevated, confirm required). vmtype: 'qemu' or 'lxc'."""
    return firewall.delete_vm_firewall_rule(
        client, node=node, vmid=vmid, pos=pos, vmtype=vmtype, confirm=confirm,
    )


@mcp.tool()
def proxmox_get_vm_firewall_options(
    node: str | None = None,
    vmid: int | None = None,
    vmtype: str = "qemu",
) -> str:
    """Get VM firewall options (read-only). vmtype: 'qemu' or 'lxc'."""
    return firewall.get_vm_firewall_options(client, node=node, vmid=vmid, vmtype=vmtype)


@mcp.tool()
def proxmox_get_vm_firewall_alias(
    node: str | None = None,
    vmid: int | None = None,
    name: str = "",
    vmtype: str = "qemu",
) -> str:
    """Get a VM firewall alias (read-only). vmtype: 'qemu' or 'lxc'."""
    return firewall.get_vm_firewall_alias(client, node=node, vmid=vmid, name=name, vmtype=vmtype)


@mcp.tool()
def proxmox_create_vm_firewall_alias(
    node: str | None = None,
    vmid: int | None = None,
    name: str = "",
    cidr: str = "",
    vmtype: str = "qemu",
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a VM firewall alias (elevated, confirm required). vmtype: 'qemu' or 'lxc'."""
    return firewall.create_vm_firewall_alias(
        client, node=node, vmid=vmid, name=name, cidr=cidr,
        vmtype=vmtype, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_vm_firewall_alias(
    node: str | None = None,
    vmid: int | None = None,
    name: str = "",
    vmtype: str = "qemu",
    confirm: bool = False,
) -> str:
    """Delete a VM firewall alias (elevated, confirm required). vmtype: 'qemu' or 'lxc'."""
    return firewall.delete_vm_firewall_alias(
        client, node=node, vmid=vmid, name=name, vmtype=vmtype, confirm=confirm,
    )


@mcp.tool()
def proxmox_list_vm_firewall_ipsets(
    node: str | None = None,
    vmid: int | None = None,
    vmtype: str = "qemu",
) -> str:
    """List VM firewall IPSets (read-only). vmtype: 'qemu' or 'lxc'."""
    return firewall.list_vm_firewall_ipsets(client, node=node, vmid=vmid, vmtype=vmtype)


@mcp.tool()
def proxmox_get_vm_firewall_rule(
    node: str | None = None,
    vmid: int | None = None,
    pos: int = 0,
    vmtype: str = "qemu",
) -> str:
    """Get a specific VM firewall rule by position (read-only). vmtype: 'qemu' or 'lxc'."""
    return firewall.get_vm_firewall_rule(client, node=node, vmid=vmid, pos=pos, vmtype=vmtype)


@mcp.tool()
def proxmox_update_vm_firewall_rule(
    node: str | None = None,
    vmid: int | None = None,
    pos: int = 0,
    vmtype: str = "qemu",
    action: str | None = None,
    dptype: str | None = None,
    dport: str | None = None,
    sport: str | None = None,
    proto: str | None = None,
    source: str | None = None,
    dest: str | None = None,
    iface: str | None = None,
    comment: str | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update a VM firewall rule (elevated). vmtype: 'qemu' or 'lxc'. Requires confirm=true."""
    return firewall.update_vm_firewall_rule(
        client, node=node, vmid=vmid, pos=pos, vmtype=vmtype,
        action=action, dptype=dptype, dport=dport, sport=sport,
        proto=proto, source=source, dest=dest,
        iface=iface, comment=comment, confirm=confirm, **kwargs,
    )


@mcp.tool()
def proxmox_set_vm_firewall_options(
    node: str | None = None,
    vmid: int | None = None,
    vmtype: str = "qemu",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Set VM firewall options (elevated). vmtype: 'qemu' or 'lxc'. Requires confirm=true."""
    return firewall.set_vm_firewall_options(client, node=node, vmid=vmid, vmtype=vmtype, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_list_vm_firewall_aliases(
    node: str | None = None,
    vmid: int | None = None,
    vmtype: str = "qemu",
) -> str:
    """List VM firewall aliases (read-only). vmtype: 'qemu' or 'lxc'."""
    return firewall.list_vm_firewall_aliases(client, node=node, vmid=vmid, vmtype=vmtype)


@mcp.tool()
def proxmox_update_vm_firewall_alias(
    node: str | None = None,
    vmid: int | None = None,
    name: str = "",
    cidr: str | None = None,
    vmtype: str = "qemu",
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Update a VM firewall alias (elevated). vmtype: 'qemu' or 'lxc'. Requires confirm=true."""
    return firewall.update_vm_firewall_alias(
        client, node=node, vmid=vmid, name=name,
        cidr=cidr, vmtype=vmtype, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_vm_firewall_log(
    node: str | None = None,
    vmid: int | None = None,
    vmtype: str = "qemu",
) -> str:
    """Read VM firewall log (read-only). vmtype: 'qemu' or 'lxc'."""
    return firewall.vm_firewall_log(client, node=node, vmid=vmid, vmtype=vmtype)


@mcp.tool()
def proxmox_vm_firewall_refs(
    node: str | None = None,
    vmid: int | None = None,
    vmtype: str = "qemu",
) -> str:
    """List VM firewall IPSet/Alias references (read-only). vmtype: 'qemu' or 'lxc'."""
    return firewall.vm_firewall_refs(client, node=node, vmid=vmid, vmtype=vmtype)


@mcp.tool()
def proxmox_list_vm_firewall_ipset_content(
    node: str | None = None,
    vmid: int | None = None,
    name: str = "",
    vmtype: str = "qemu",
) -> str:
    """List VM firewall IPSet content (read-only). vmtype: 'qemu' or 'lxc'."""
    return firewall.list_vm_firewall_ipset_content(client, node=node, vmid=vmid, name=name, vmtype=vmtype)


@mcp.tool()
def proxmox_create_vm_firewall_ipset(
    node: str | None = None,
    vmid: int | None = None,
    name: str = "",
    vmtype: str = "qemu",
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a VM firewall IPSet (elevated). vmtype: 'qemu' or 'lxc'. Requires confirm=true."""
    return firewall.create_vm_firewall_ipset(
        client, node=node, vmid=vmid,
        name=name, vmtype=vmtype, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_vm_firewall_ipset(
    node: str | None = None,
    vmid: int | None = None,
    name: str = "",
    vmtype: str = "qemu",
    confirm: bool = False,
) -> str:
    """Delete a VM firewall IPSet (elevated). vmtype: 'qemu' or 'lxc'. Requires confirm=true."""
    return firewall.delete_vm_firewall_ipset(client, node=node, vmid=vmid, name=name, vmtype=vmtype, confirm=confirm)


@mcp.tool()
def proxmox_add_vm_firewall_ipset_entry(
    node: str | None = None,
    vmid: int | None = None,
    name: str = "",
    cidr: str = "",
    vmtype: str = "qemu",
    comment: str | None = None,
    nomatch: int | None = None,
    confirm: bool = False,
) -> str:
    """Add IP/CIDR entry to VM firewall IPSet (elevated). vmtype: 'qemu' or 'lxc'. Requires confirm=true."""
    return firewall.add_vm_firewall_ipset_entry(
        client, node=node, vmid=vmid, name=name, cidr=cidr,
        vmtype=vmtype, comment=comment, nomatch=nomatch, confirm=confirm,
    )


@mcp.tool()
def proxmox_get_vm_firewall_ipset_entry(
    node: str | None = None,
    vmid: int | None = None,
    name: str = "",
    cidr: str = "",
    vmtype: str = "qemu",
) -> str:
    """Get a specific VM firewall IPSet entry (read-only). vmtype: 'qemu' or 'lxc'."""
    return firewall.get_vm_firewall_ipset_entry(client, node=node, vmid=vmid, name=name, cidr=cidr, vmtype=vmtype)


@mcp.tool()
def proxmox_update_vm_firewall_ipset_entry(
    node: str | None = None,
    vmid: int | None = None,
    name: str = "",
    cidr: str = "",
    vmtype: str = "qemu",
    comment: str | None = None,
    nomatch: int | None = None,
    confirm: bool = False,
) -> str:
    """Update a VM firewall IPSet entry (elevated). vmtype: 'qemu' or 'lxc'. Requires confirm=true."""
    return firewall.update_vm_firewall_ipset_entry(
        client, node=node, vmid=vmid, name=name, cidr=cidr,
        vmtype=vmtype, comment=comment, nomatch=nomatch, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_vm_firewall_ipset_entry(
    node: str | None = None,
    vmid: int | None = None,
    name: str = "",
    cidr: str = "",
    vmtype: str = "qemu",
    confirm: bool = False,
) -> str:
    """Delete a VM firewall IPSet entry (elevated). vmtype: 'qemu' or 'lxc'. Requires confirm=true."""
    return firewall.delete_vm_firewall_ipset_entry(
        client, node=node, vmid=vmid,
        name=name, cidr=cidr, vmtype=vmtype, confirm=confirm,
    )


@mcp.tool()
def proxmox_list_cluster_firewall_ipset_content(name: str = "") -> str:
    """List cluster firewall IPSet content (read-only)."""
    return firewall.list_cluster_firewall_ipset_content(client, name=name)


@mcp.tool()
def proxmox_create_cluster_firewall_ipset(
    name: str = "",
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a cluster firewall IPSet (elevated, confirm required)."""
    return firewall.create_cluster_firewall_ipset(client, name=name, comment=comment, confirm=confirm)


@mcp.tool()
def proxmox_delete_cluster_firewall_ipset(
    name: str = "",
    confirm: bool = False,
) -> str:
    """Delete a cluster firewall IPSet (elevated, confirm required)."""
    return firewall.delete_cluster_firewall_ipset(client, name=name, confirm=confirm)


@mcp.tool()
def proxmox_get_cluster_firewall_alias(name: str = "") -> str:
    """Get a cluster firewall alias (read-only)."""
    return firewall.get_cluster_firewall_alias(client, name=name)


@mcp.tool()
def proxmox_update_cluster_firewall_alias(
    name: str = "",
    cidr: str | None = None,
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Update a cluster firewall alias (elevated, confirm required)."""
    return firewall.update_cluster_firewall_alias(client, name=name, cidr=cidr, comment=comment, confirm=confirm)


@mcp.tool()
def proxmox_update_cluster_firewall_ipset(
    name: str = "",
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Update a cluster firewall IPSet (elevated, confirm required)."""
    return firewall.update_cluster_firewall_ipset(client, name=name, comment=comment, confirm=confirm)


@mcp.tool()
def proxmox_add_cluster_firewall_ipset_entry(
    name: str = "",
    cidr: str = "",
    comment: str | None = None,
    nomatch: int | None = None,
    confirm: bool = False,
) -> str:
    """Add an entry to a cluster firewall IPSet (elevated, confirm required)."""
    return firewall.add_cluster_firewall_ipset_entry(
        client, name=name, cidr=cidr, comment=comment, nomatch=nomatch, confirm=confirm,
    )


@mcp.tool()
def proxmox_get_cluster_firewall_ipset_entry(
    name: str = "",
    cidr: str = "",
) -> str:
    """Get a cluster firewall IPSet entry (read-only)."""
    return firewall.get_cluster_firewall_ipset_entry(client, name=name, cidr=cidr)


@mcp.tool()
def proxmox_delete_cluster_firewall_ipset_entry(
    name: str = "",
    cidr: str = "",
    confirm: bool = False,
) -> str:
    """Delete an entry from a cluster firewall IPSet (elevated, confirm required)."""
    return firewall.delete_cluster_firewall_ipset_entry(client, name=name, cidr=cidr, confirm=confirm)


@mcp.tool()
def proxmox_list_cluster_firewall_macros() -> str:
    """List cluster firewall macros (read-only)."""
    return firewall.list_cluster_firewall_macros(client)


@mcp.tool()
def proxmox_list_node_firewall_aliases(node: str | None = None) -> str:
    """List node firewall aliases (read-only)."""
    return firewall.list_node_firewall_aliases(client, node=node)


@mcp.tool()
def proxmox_node_firewall_log(node: str | None = None) -> str:
    """Get node firewall log (read-only)."""
    return firewall.node_firewall_log(client, node=node)


@mcp.tool()
def proxmox_get_node_firewall_rule(
    node: str | None = None,
    pos: int = 0,
) -> str:
    """Get a specific node firewall rule (read-only)."""
    return firewall.get_node_firewall_rule(client, node=node, pos=pos)


@mcp.tool()
def proxmox_update_node_firewall_rule(
    node: str | None = None,
    pos: int = 0,
    action: str | None = None,
    dptype: str | None = None,
    dport: str | None = None,
    sport: str | None = None,
    proto: str | None = None,
    source: str | None = None,
    dest: str | None = None,
    iface: str | None = None,
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Update a node firewall rule (elevated, confirm required)."""
    return firewall.update_node_firewall_rule(
        client, node=node, pos=pos, action=action, dptype=dptype, dport=dport,
        sport=sport, proto=proto, source=source, dest=dest,
        iface=iface, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_set_node_firewall_options(
    node: str | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Set node firewall options (elevated, confirm required)."""
    return firewall.set_node_firewall_options(client, node=node, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_list_node_firewall_ipsets(node: str | None = None) -> str:
    """List node firewall IPSets (read-only)."""
    return firewall.list_node_firewall_ipsets(client, node=node)


@mcp.tool()
def proxmox_list_ha_resources() -> str:
    """List HA resources in the cluster (read-only)."""
    return ha.list_ha_resources(client)


@mcp.tool()
def proxmox_create_ha_resource(
    sid: str = "",
    group: str | None = None,
    comment: str | None = None,
    max_relocate: int | None = None,
    max_restart: int | None = None,
    state: str | None = None,
    type: str | None = None,
    confirm: bool = False,
) -> str:
    """Create an HA resource (elevated, confirm required)."""
    return ha.create_ha_resource(
        client, sid=sid, group=group, comment=comment,
        max_relocate=max_relocate, max_restart=max_restart,
        state=state, type=type, confirm=confirm,
    )


@mcp.tool()
def proxmox_get_ha_resource(sid: str = "") -> str:
    """Get HA resource configuration (read-only)."""
    return ha.get_ha_resource(client, sid=sid)


@mcp.tool()
def proxmox_update_ha_resource(
    sid: str = "",
    group: str | None = None,
    comment: str | None = None,
    max_relocate: int | None = None,
    max_restart: int | None = None,
    state: str | None = None,
    confirm: bool = False,
) -> str:
    """Update an HA resource (elevated, confirm required)."""
    return ha.update_ha_resource(
        client, sid=sid, group=group, comment=comment,
        max_relocate=max_relocate, max_restart=max_restart,
        state=state, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_ha_resource(
    sid: str = "",
    confirm: bool = False,
) -> str:
    """Delete an HA resource (elevated, confirm required)."""
    return ha.delete_ha_resource(client, sid=sid, confirm=confirm)


@mcp.tool()
def proxmox_migrate_ha_resource(
    sid: str = "",
    node: str = "",
    confirm: bool = False,
) -> str:
    """Migrate an HA resource to another node (elevated, confirm required)."""
    return ha.migrate_ha_resource(client, sid=sid, node=node, confirm=confirm)


@mcp.tool()
def proxmox_relocate_ha_resource(
    sid: str = "",
    node: str = "",
    confirm: bool = False,
) -> str:
    """Relocate an HA resource to another node (elevated, confirm required)."""
    return ha.relocate_ha_resource(client, sid=sid, node=node, confirm=confirm)


@mcp.tool()
def proxmox_list_ha_groups() -> str:
    """List HA groups (read-only)."""
    return ha.list_ha_groups(client)


@mcp.tool()
def proxmox_ha_status() -> str:
    """Get HA manager status (read-only)."""
    return ha.ha_status(client)


@mcp.tool()
def proxmox_list_replication() -> str:
    """List replication jobs in the cluster (read-only)."""
    return replication.list_replication(client)


@mcp.tool()
def proxmox_create_replication(
    id: str = "",
    source: str | None = None,
    target: str | None = None,
    schedule: str | None = None,
    comment: str | None = None,
    disable: bool | None = None,
    rate: float | None = None,
    confirm: bool = False,
) -> str:
    """Create a replication job (elevated, confirm required)."""
    return replication.create_replication(
        client, id=id, source=source, target=target,
        schedule=schedule, comment=comment, disable=disable,
        rate=rate, confirm=confirm,
    )


@mcp.tool()
def proxmox_get_replication(id: str = "") -> str:
    """Get replication job configuration (read-only)."""
    return replication.get_replication(client, id=id)


@mcp.tool()
def proxmox_update_replication(
    id: str = "",
    source: str | None = None,
    target: str | None = None,
    schedule: str | None = None,
    comment: str | None = None,
    disable: bool | None = None,
    rate: float | None = None,
    confirm: bool = False,
) -> str:
    """Update a replication job (elevated, confirm required)."""
    return replication.update_replication(
        client, id=id, source=source, target=target,
        schedule=schedule, comment=comment, disable=disable,
        rate=rate, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_replication(
    id: str = "",
    confirm: bool = False,
) -> str:
    """Delete a replication job (elevated, confirm required)."""
    return replication.delete_replication(client, id=id, confirm=confirm)


@mcp.tool()
def proxmox_list_node_replication(node: str | None = None) -> str:
    """List replication jobs on a node (read-only)."""
    return replication.list_node_replication(client, node=node)


@mcp.tool()
def proxmox_schedule_replication(
    node: str | None = None,
    id: str = "",
    confirm: bool = False,
) -> str:
    """Schedule a replication job now (elevated, confirm required)."""
    return replication.schedule_replication(client, node=node, id=id, confirm=confirm)


@mcp.tool()
def proxmox_get_replication_status(
    node: str | None = None,
    id: str = "",
) -> str:
    """Get replication job status on a node (read-only)."""
    return replication.get_replication_status(client, node=node, id=id)


@mcp.tool()
def proxmox_get_replication_log(
    node: str | None = None,
    id: str = "",
) -> str:
    """Get replication job log on a node (read-only)."""
    return replication.get_replication_log(client, node=node, id=id)


@mcp.tool()
def proxmox_list_disks(node: str | None = None) -> str:
    """List local disks on a node (read-only)."""
    return disks.list_disks(client, node=node)


@mcp.tool()
def proxmox_get_disk_smart(
    node: str | None = None,
    disk: str = "",
) -> str:
    """Get SMART health of a disk (read-only)."""
    return disks.get_disk_smart(client, node=node, disk=disk)


@mcp.tool()
def proxmox_list_lvm(node: str | None = None) -> str:
    """List LVM volume groups on a node (read-only)."""
    return disks.list_lvm(client, node=node)


@mcp.tool()
def proxmox_list_lvmthin(node: str | None = None) -> str:
    """List LVM thin pools on a node (read-only)."""
    return disks.list_lvmthin(client, node=node)


@mcp.tool()
def proxmox_list_zfs(node: str | None = None) -> str:
    """List ZFS pools on a node (read-only)."""
    return disks.list_zfs(client, node=node)


@mcp.tool()
def proxmox_init_gpt(
    node: str | None = None,
    disk: str = "",
    confirm: bool = False,
) -> str:
    """Initialize a disk with GPT (elevated, confirm required)."""
    return disks.init_gpt(client, node=node, disk=disk, confirm=confirm)


@mcp.tool()
def proxmox_wipe_disk(
    node: str | None = None,
    disk: str = "",
    confirm: bool = False,
) -> str:
    """Wipe a disk (elevated, confirm required)."""
    return disks.wipe_disk(client, node=node, disk=disk, confirm=confirm)


@mcp.tool()
def proxmox_zfs_detail(
    node: str | None = None,
    name: str = "",
) -> str:
    """Get ZFS pool details (read-only)."""
    return disks.zfs_detail(client, node=node, name=name)


@mcp.tool()
def proxmox_zfs_create(
    node: str | None = None,
    name: str = "",
    devices: str = "",
    raidlevel: str | None = None,
    ashift: int | None = None,
    confirm: bool = False,
) -> str:
    """Create a ZFS pool (elevated, confirm required)."""
    return disks.zfs_create(
        client, node=node, name=name, devices=devices,
        raidlevel=raidlevel, ashift=ashift, confirm=confirm,
    )


@mcp.tool()
def proxmox_zfs_destroy(
    node: str | None = None,
    name: str = "",
    confirm: bool = False,
) -> str:
    """Destroy a ZFS pool (elevated, confirm required)."""
    return disks.zfs_destroy(client, node=node, name=name, confirm=confirm)


@mcp.tool()
def proxmox_lvm_create(
    node: str | None = None,
    name: str = "",
    devices: str = "",
    confirm: bool = False,
) -> str:
    """Create an LVM volume group (elevated, confirm required)."""
    return disks.lvm_create(client, node=node, name=name, devices=devices, confirm=confirm)


@mcp.tool()
def proxmox_lvm_detail(
    node: str | None = None,
    name: str = "",
) -> str:
    """Get LVM volume group details (read-only)."""
    return disks.lvm_detail(client, node=node, name=name)


@mcp.tool()
def proxmox_lvm_destroy(
    node: str | None = None,
    name: str = "",
    confirm: bool = False,
) -> str:
    """Destroy an LVM volume group (elevated, confirm required)."""
    return disks.lvm_destroy(client, node=node, name=name, confirm=confirm)


@mcp.tool()
def proxmox_lvmthin_create(
    node: str | None = None,
    name: str = "",
    devices: str = "",
    confirm: bool = False,
) -> str:
    """Create an LVM thin pool (elevated, confirm required)."""
    return disks.lvmthin_create(client, node=node, name=name, devices=devices, confirm=confirm)


@mcp.tool()
def proxmox_lvmthin_destroy(
    node: str | None = None,
    name: str = "",
    confirm: bool = False,
) -> str:
    """Destroy an LVM thin pool (elevated, confirm required)."""
    return disks.lvmthin_destroy(client, node=node, name=name, confirm=confirm)


@mcp.tool()
def proxmox_directory_list(node: str | None = None) -> str:
    """List PVE managed directory storages (read-only)."""
    return disks.directory_list(client, node=node)


@mcp.tool()
def proxmox_directory_create(
    node: str | None = None,
    name: str = "",
    devices: str = "",
    confirm: bool = False,
) -> str:
    """Create a directory storage on a disk (elevated, confirm required)."""
    return disks.directory_create(client, node=node, name=name, devices=devices, confirm=confirm)


@mcp.tool()
def proxmox_directory_destroy(
    node: str | None = None,
    name: str = "",
    confirm: bool = False,
) -> str:
    """Destroy a directory storage (elevated, confirm required)."""
    return disks.directory_destroy(client, node=node, name=name, confirm=confirm)


@mcp.tool()
def proxmox_list_pci(node: str | None = None) -> str:
    """List PCI devices on a node (read-only)."""
    return hardware.list_pci(client, node=node)


@mcp.tool()
def proxmox_list_usb(node: str | None = None) -> str:
    """List USB devices on a node (read-only)."""
    return hardware.list_usb(client, node=node)


@mcp.tool()
def proxmox_get_pci_device(
    node: str | None = None,
    pciid: str = "",
) -> str:
    """Get PCI device details (read-only)."""
    return hardware.get_pci_device(client, node=node, pciid=pciid)


@mcp.tool()
def proxmox_list_pci_mdev(
    node: str | None = None,
    pciid: str = "",
) -> str:
    """List mediated device types for a PCI device (read-only)."""
    return hardware.list_pci_mdev(client, node=node, pciid=pciid)


@mcp.tool()
def proxmox_cloudinit_dump(
    node: str | None = None,
    vmid: int | None = None,
    type: str | None = None,
) -> str:
    """Dump cloud-init configuration for a VM (read-only)."""
    return cloudinit.cloudinit_dump(client, node=node, vmid=vmid, type=type)


@mcp.tool()
def proxmox_node_version(node: str | None = None) -> str:
    """Get Proxmox VE version on a node (read-only)."""
    return discovery.node_version(client, node=node)


@mcp.tool()
def proxmox_node_dns_discovery(node: str | None = None) -> str:
    """Get DNS settings for a node via discovery (read-only)."""
    return discovery.node_dns(client, node=node)


@mcp.tool()
def proxmox_node_hosts_discovery(node: str | None = None) -> str:
    """Get hosts file content for a node via discovery (read-only)."""
    return discovery.node_hosts(client, node=node)


@mcp.tool()
def proxmox_node_time(node: str | None = None) -> str:
    """Get node time and timezone (read-only)."""
    return discovery.node_time(client, node=node)


@mcp.tool()
def proxmox_node_syslog(
    node: str | None = None,
    limit: int | None = None,
    start: int | None = None,
    since: str | None = None,
    until: str | None = None,
) -> str:
    """Get node syslog entries (read-only)."""
    return discovery.node_syslog(client, node=node, limit=limit, start=start, since=since, until=until)


@mcp.tool()
def proxmox_node_journal(
    node: str | None = None,
    limit: int | None = None,
    since: str | None = None,
    until: str | None = None,
    service: str | None = None,
) -> str:
    """Get node journal log entries (read-only)."""
    return discovery.node_journal(client, node=node, limit=limit, since=since, until=until, service=service)


@mcp.tool()
def proxmox_cluster_log(limit: int | None = None) -> str:
    """Get cluster log entries (read-only)."""
    return discovery.cluster_log(client, limit=limit)


@mcp.tool()
def proxmox_stop_task(
    node: str | None = None,
    upid: str = "",
    confirm: bool = False,
) -> str:
    """Stop a running task (elevated, confirm required)."""
    return tasks.stop_task(client, node=node, upid=upid, confirm=confirm)


@mcp.tool()
def proxmox_list_acme_accounts() -> str:
    """List ACME accounts (read-only)."""
    return acme.list_acme_accounts(client)


@mcp.tool()
def proxmox_get_acme_account(name: str = "") -> str:
    """Get ACME account details (read-only)."""
    return acme.get_acme_account(client, name=name)


@mcp.tool()
def proxmox_create_acme_account(
    name: str = "",
    contact: str = "",
    directory: str | None = None,
    confirm: bool = False,
) -> str:
    """Create an ACME account (elevated, confirm required)."""
    return acme.create_acme_account(
        client, name=name, contact=contact, directory=directory, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_acme_account(
    name: str = "",
    confirm: bool = False,
) -> str:
    """Delete an ACME account (elevated, confirm required)."""
    return acme.delete_acme_account(client, name=name, confirm=confirm)


@mcp.tool()
def proxmox_update_acme_account(
    name: str = "",
    contact: str | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update an ACME account (elevated, confirm required)."""
    return acme.update_acme_account(client, name=name, contact=contact, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_list_acme_directories() -> str:
    """List ACME directories (read-only)."""
    return acme.list_acme_directories(client)


@mcp.tool()
def proxmox_list_acme_plugins() -> str:
    """List ACME plugins (read-only)."""
    return acme.list_acme_plugins(client)


@mcp.tool()
def proxmox_create_acme_plugin(
    id: str = "",
    type: str = "",
    confirm: bool = False,
) -> str:
    """Create an ACME plugin (elevated, confirm required)."""
    return acme.create_acme_plugin(client, id=id, type=type, confirm=confirm)


@mcp.tool()
def proxmox_delete_acme_plugin(
    id: str = "",
    confirm: bool = False,
) -> str:
    """Delete an ACME plugin (elevated, confirm required)."""
    return acme.delete_acme_plugin(client, id=id, confirm=confirm)


@mcp.tool()
def proxmox_update_acme_plugin(
    id: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update an ACME plugin (elevated, confirm required)."""
    return acme.update_acme_plugin(client, id=id, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_get_acme_plugin(id: str = "") -> str:
    """Get ACME plugin configuration (read-only)."""
    return acme.get_acme_plugin(client, id=id)


@mcp.tool()
def proxmox_acme_meta() -> str:
    """Get ACME directory meta information (read-only)."""
    return acme.acme_meta(client)


@mcp.tool()
def proxmox_cluster_config() -> str:
    """Get cluster corosync config (read-only)."""
    return cluster.cluster_config(client)


@mcp.tool()
def proxmox_cluster_config_nodes() -> str:
    """Get cluster config nodes (read-only)."""
    return cluster.cluster_config_nodes(client)


@mcp.tool()
def proxmox_cluster_config_join() -> str:
    """Get cluster join info (read-only)."""
    return cluster.cluster_config_join(client)


@mcp.tool()
def proxmox_get_backup_job(id: str = "") -> str:
    """Get backup job configuration (read-only)."""
    return cluster.get_backup_job(client, id=id)


@mcp.tool()
def proxmox_update_backup_job(
    id: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update a backup job (elevated, confirm required)."""
    return cluster.update_backup_job(client, id=id, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_backup_info_not_backed_up() -> str:
    """List guests not covered by any backup job (read-only)."""
    return cluster.backup_info_not_backed_up(client)


@mcp.tool()
def proxmox_api_version() -> str:
    """Get Proxmox API version (read-only)."""
    return cluster.api_version(client)


@mcp.tool()
def proxmox_cluster_config_totem() -> str:
    """Get cluster corosync totem config (read-only)."""
    return cluster.cluster_config_totem(client)


@mcp.tool()
def proxmox_cluster_config_qdevice() -> str:
    """Get cluster QDevice status (read-only)."""
    return cluster.cluster_config_qdevice(client)


@mcp.tool()
def proxmox_backup_info_index() -> str:
    """Get backup info index (read-only)."""
    return cluster.backup_info_index(client)


@mcp.tool()
def proxmox_backup_job_included_volumes(id: str = "") -> str:
    """Get backup job included volumes (read-only)."""
    return cluster.backup_job_included_volumes(client, id=id)


@mcp.tool()
def proxmox_update_dns(
    node: str | None = None,
    dns1: str | None = None,
    dns2: str | None = None,
    search: str | None = None,
    confirm: bool = False,
) -> str:
    """Update DNS settings for a node (elevated, confirm required)."""
    return nodes.update_dns(client, node=node, dns1=dns1, dns2=dns2, search=search, confirm=confirm)


@mcp.tool()
def proxmox_update_hosts(
    node: str | None = None,
    data: str = "",
    confirm: bool = False,
) -> str:
    """Update hosts file for a node (elevated, confirm required)."""
    return nodes.update_hosts(client, node=node, data=data, confirm=confirm)


@mcp.tool()
def proxmox_update_time(
    node: str | None = None,
    timezone: str | None = None,
    confirm: bool = False,
) -> str:
    """Update timezone for a node (elevated, confirm required)."""
    return nodes.update_time(client, node=node, timezone=timezone, confirm=confirm)


@mcp.tool()
def proxmox_vzdump_defaults(
    node: str | None = None,
    storage: str | None = None,
) -> str:
    """Get VZDump backup defaults for a node (read-only)."""
    return nodes.vzdump_defaults(client, node=node, storage=storage)


@mcp.tool()
def proxmox_extract_backup_config(
    node: str | None = None,
    archive: str = "",
) -> str:
    """Extract config from a backup archive (read-only)."""
    return nodes.extract_backup_config(client, node=node, archive=archive)


@mcp.tool()
def proxmox_get_volume_info(
    node: str | None = None,
    storage: str = "local",
    volume: str = "",
) -> str:
    """Get detailed volume info (read-only)."""
    return storage_mod.get_volume_info(client, node=node, storage=storage, volume=volume)


@mcp.tool()
def proxmox_node_storage_list(node: str | None = None) -> str:
    """List all storage on a node (read-only)."""
    return storage_mod.node_storage_list(client, node=node)


@mcp.tool()
def proxmox_scan_nfs(
    node: str | None = None,
    server: str = "",
) -> str:
    """Scan for NFS exports on a remote server."""
    return nodes.scan_nfs(client, node=node, server=server)


@mcp.tool()
def proxmox_scan_iscsi(
    node: str | None = None,
    server: str = "",
) -> str:
    """Scan for iSCSI targets on a remote server."""
    return nodes.scan_iscsi(client, node=node, server=server)


@mcp.tool()
def proxmox_scan_lvm(node: str | None = None) -> str:
    """List LVM volume groups on a node."""
    return nodes.scan_lvm(client, node=node)


@mcp.tool()
def proxmox_scan_lvmthin(node: str | None = None) -> str:
    """List LVM thin pools on a node."""
    return nodes.scan_lvmthin(client, node=node)


@mcp.tool()
def proxmox_scan_cifs(
    node: str | None = None,
    server: str = "",
) -> str:
    """Scan for CIFS shares on a remote server."""
    return nodes.scan_cifs(client, node=node, server=server)


@mcp.tool()
def proxmox_scan_zfs(node: str | None = None) -> str:
    """List ZFS pools on a node."""
    return nodes.scan_zfs(client, node=node)


@mcp.tool()
def proxmox_scan_pbs(
    node: str | None = None,
    server: str = "",
    username: str | None = None,
    password: str | None = None,
) -> str:
    """Scan for Proxmox Backup Server datastores."""
    return nodes.scan_pbs(client, node=node, server=server, username=username, password=password)


@mcp.tool()
def proxmox_get_subscription(node: str | None = None) -> str:
    """Get node subscription info (read-only)."""
    return nodes.get_subscription(client, node=node)


@mcp.tool()
def proxmox_update_subscription(
    node: str | None = None,
    key: str = "",
    confirm: bool = False,
) -> str:
    """Set subscription key on a node (elevated, confirm required)."""
    return nodes.update_subscription(client, node=node, key=key, confirm=confirm)


@mcp.tool()
def proxmox_node_report(node: str | None = None) -> str:
    """Get system report for a node (read-only)."""
    return nodes.node_report(client, node=node)


@mcp.tool()
def proxmox_node_execute(
    node: str | None = None,
    commands: str | None = None,
    confirm: bool = False,
) -> str:
    """Execute commands on a node (elevated, confirm required, DANGEROUS)."""
    return nodes.node_execute(client, node=node, commands=commands, confirm=confirm)


@mcp.tool()
def proxmox_get_network_interface(
    node: str | None = None,
    iface: str = "",
) -> str:
    """Get details of a single network interface on a node (read-only)."""
    return nodes.get_network_interface(client, node=node, iface=iface)


@mcp.tool()
def proxmox_bulk_migrate_guests(
    vmids: str = "",
    target: str = "",
    confirm: bool = False,
) -> str:
    """Bulk migrate guests to another node (elevated, confirm required)."""
    return cluster.bulk_migrate_guests(client, vmids=vmids, target=target, confirm=confirm)


@mcp.tool()
def proxmox_bulk_shutdown_guests(
    vmids: str = "",
    confirm: bool = False,
) -> str:
    """Bulk shutdown guests across the cluster (elevated, confirm required)."""
    return cluster.bulk_shutdown_guests(client, vmids=vmids, confirm=confirm)


@mcp.tool()
def proxmox_node_ceph_fs(node: str | None = None) -> str:
    """List Ceph filesystems on a node (read-only)."""
    return ceph.node_ceph_fs(client, node=node)


@mcp.tool()
def proxmox_create_ceph_fs(
    node: str | None = None,
    name: str = "",
    confirm: bool = False,
) -> str:
    """Create a Ceph filesystem (elevated, confirm required)."""
    return ceph.create_ceph_fs(client, node=node, name=name, confirm=confirm)


@mcp.tool()
def proxmox_list_ceph_osd(node: str | None = None) -> str:
    """List Ceph OSDs on a node (read-only)."""
    return ceph.list_ceph_osd(client, node=node)


@mcp.tool()
def proxmox_list_ceph_mon(node: str | None = None) -> str:
    """List Ceph monitors on a node (read-only)."""
    return ceph.list_ceph_mon(client, node=node)


@mcp.tool()
def proxmox_list_ceph_mgr(node: str | None = None) -> str:
    """List Ceph managers on a node (read-only)."""
    return ceph.list_ceph_mgr(client, node=node)


@mcp.tool()
def proxmox_ceph_config(node: str | None = None) -> str:
    """Get raw Ceph configuration on a node (read-only)."""
    return ceph.ceph_config(client, node=node)


@mcp.tool()
def proxmox_ceph_flags() -> str:
    """Get Ceph cluster flags (read-only)."""
    return ceph.ceph_flags(client)


@mcp.tool()
def proxmox_set_ceph_flags(
    flags: str = "",
    confirm: bool = False,
) -> str:
    """Set Ceph cluster flags (elevated, confirm required)."""
    return ceph.set_ceph_flags(client, flags=flags, confirm=confirm)


@mcp.tool()
def proxmox_get_ceph_flag(flag: str = "") -> str:
    """Get a specific Ceph cluster flag (read-only)."""
    return ceph.get_ceph_flag(client, flag=flag)


@mcp.tool()
def proxmox_set_ceph_flag(
    flag: str = "",
    value: str = "",
    confirm: bool = False,
) -> str:
    """Set a specific Ceph cluster flag (elevated, confirm required)."""
    return ceph.set_ceph_flag(client, flag=flag, value=value, confirm=confirm)


@mcp.tool()
def proxmox_list_ceph_osd_detail(
    node: str | None = None,
    osdid: int = 0,
) -> str:
    """Get Ceph OSD detail (read-only)."""
    return ceph.list_ceph_osd_detail(client, node=node, osdid=osdid)


@mcp.tool()
def proxmox_create_ceph_osd(
    node: str | None = None,
    dev: str = "",
    confirm: bool = False,
) -> str:
    """Create a Ceph OSD (elevated, confirm required)."""
    return ceph.create_ceph_osd(client, node=node, dev=dev, confirm=confirm)


@mcp.tool()
def proxmox_destroy_ceph_osd(
    node: str | None = None,
    osdid: int = 0,
    confirm: bool = False,
) -> str:
    """Destroy a Ceph OSD (elevated, confirm required)."""
    return ceph.destroy_ceph_osd(client, node=node, osdid=osdid, confirm=confirm)


@mcp.tool()
def proxmox_ceph_osd_in(
    node: str | None = None,
    osdid: int = 0,
    confirm: bool = False,
) -> str:
    """Mark Ceph OSD in (elevated, confirm required)."""
    return ceph.ceph_osd_in(client, node=node, osdid=osdid, confirm=confirm)


@mcp.tool()
def proxmox_ceph_osd_out(
    node: str | None = None,
    osdid: int = 0,
    confirm: bool = False,
) -> str:
    """Mark Ceph OSD out (elevated, confirm required)."""
    return ceph.ceph_osd_out(client, node=node, osdid=osdid, confirm=confirm)


@mcp.tool()
def proxmox_ceph_osd_scrub(
    node: str | None = None,
    osdid: int = 0,
    confirm: bool = False,
) -> str:
    """Scrub a Ceph OSD (elevated, confirm required)."""
    return ceph.ceph_osd_scrub(client, node=node, osdid=osdid, confirm=confirm)


@mcp.tool()
def proxmox_ceph_osd_metadata(
    node: str | None = None,
    osdid: int = 0,
) -> str:
    """Get Ceph OSD metadata (read-only)."""
    return ceph.ceph_osd_metadata(client, node=node, osdid=osdid)


@mcp.tool()
def proxmox_list_ceph_pools(node: str | None = None) -> str:
    """List Ceph pools on a node (read-only)."""
    return ceph.list_ceph_pools(client, node=node)


@mcp.tool()
def proxmox_create_ceph_pool(
    node: str | None = None,
    name: str = "",
    confirm: bool = False,
    pg_num: int | None = None,
    size: int | None = None,
    min_size: int | None = None,
) -> str:
    """Create a Ceph pool (elevated, confirm required)."""
    return ceph.create_ceph_pool(
        client, node=node, name=name, confirm=confirm,
        pg_num=pg_num, size=size, min_size=min_size,
    )


@mcp.tool()
def proxmox_get_ceph_pool(node: str | None = None, name: str = "") -> str:
    """Get Ceph pool details (read-only)."""
    return ceph.get_ceph_pool(client, node=node, name=name)


@mcp.tool()
def proxmox_update_ceph_pool(
    node: str | None = None,
    name: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update a Ceph pool (elevated, confirm required)."""
    return ceph.update_ceph_pool(client, node=node, name=name, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_destroy_ceph_pool(
    node: str | None = None,
    name: str = "",
    confirm: bool = False,
) -> str:
    """Destroy a Ceph pool (elevated, confirm required)."""
    return ceph.destroy_ceph_pool(client, node=node, name=name, confirm=confirm)


@mcp.tool()
def proxmox_ceph_pool_status(node: str | None = None, name: str = "") -> str:
    """Get Ceph pool status (read-only)."""
    return ceph.ceph_pool_status(client, node=node, name=name)


@mcp.tool()
def proxmox_list_ceph_mds_detail(node: str | None = None) -> str:
    """List Ceph MDS detail on a node (read-only)."""
    return ceph.list_ceph_mds_detail(client, node=node)


@mcp.tool()
def proxmox_create_ceph_mds(
    node: str | None = None,
    name: str = "",
    confirm: bool = False,
) -> str:
    """Create Ceph MDS (elevated, confirm required)."""
    return ceph.create_ceph_mds(client, node=node, name=name, confirm=confirm)


@mcp.tool()
def proxmox_destroy_ceph_mds(
    node: str | None = None,
    name: str = "",
    confirm: bool = False,
) -> str:
    """Destroy Ceph MDS (elevated, confirm required)."""
    return ceph.destroy_ceph_mds(client, node=node, name=name, confirm=confirm)


@mcp.tool()
def proxmox_create_ceph_mgr(
    node: str | None = None,
    id: str = "",
    confirm: bool = False,
) -> str:
    """Create Ceph MGR (elevated, confirm required)."""
    return ceph.create_ceph_mgr(client, node=node, id=id, confirm=confirm)


@mcp.tool()
def proxmox_destroy_ceph_mgr(
    node: str | None = None,
    id: str = "",
    confirm: bool = False,
) -> str:
    """Destroy Ceph MGR (elevated, confirm required)."""
    return ceph.destroy_ceph_mgr(client, node=node, id=id, confirm=confirm)


@mcp.tool()
def proxmox_create_ceph_mon(
    node: str | None = None,
    monid: str = "",
    confirm: bool = False,
) -> str:
    """Create Ceph MON (elevated, confirm required)."""
    return ceph.create_ceph_mon(client, node=node, monid=monid, confirm=confirm)


@mcp.tool()
def proxmox_destroy_ceph_mon(
    node: str | None = None,
    monid: str = "",
    confirm: bool = False,
) -> str:
    """Destroy Ceph MON (elevated, confirm required)."""
    return ceph.destroy_ceph_mon(client, node=node, monid=monid, confirm=confirm)


@mcp.tool()
def proxmox_start_ceph(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Start Ceph services on a node (elevated, confirm required)."""
    return ceph.start_ceph(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_stop_ceph(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Stop Ceph services on a node (elevated, confirm required)."""
    return ceph.stop_ceph(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_restart_ceph(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Restart Ceph services on a node (elevated, confirm required)."""
    return ceph.restart_ceph(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_ceph_cfg_db(node: str | None = None) -> str:
    """Get Ceph config database on a node (read-only)."""
    return ceph.ceph_cfg_db(client, node=node)


@mcp.tool()
def proxmox_ceph_cfg_value(
    node: str | None = None,
    name: str | None = None,
    section: str | None = None,
) -> str:
    """Get Ceph config values on a node (read-only)."""
    kwargs = {}
    if name is not None:
        kwargs["name"] = name
    if section is not None:
        kwargs["section"] = section
    return ceph.ceph_cfg_value(client, node=node, **kwargs)


@mcp.tool()
def proxmox_ceph_crush(node: str | None = None) -> str:
    """Get Ceph CRUSH map on a node (read-only)."""
    return ceph.ceph_crush(client, node=node)


@mcp.tool()
def proxmox_ceph_log(node: str | None = None) -> str:
    """Get Ceph log on a node (read-only)."""
    return ceph.ceph_log(client, node=node)


@mcp.tool()
def proxmox_init_ceph(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Initialize Ceph on a node (elevated, confirm required)."""
    return ceph.init_ceph(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_list_apt_updates(node: str | None = None) -> str:
    """List available APT updates on a node (read-only)."""
    return apt.list_updates(client, node=node)


@mcp.tool()
def proxmox_refresh_apt_updates(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Refresh APT package index (elevated, confirm required)."""
    return apt.refresh_updates(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_list_apt_repositories(node: str | None = None) -> str:
    """List APT repositories on a node (read-only)."""
    return apt.list_repositories(client, node=node)


@mcp.tool()
def proxmox_list_apt_versions(node: str | None = None) -> str:
    """List APT package versions on a node (read-only)."""
    return apt.list_versions(client, node=node)


@mcp.tool()
def proxmox_add_apt_repo(
    node: str | None = None,
    path: str | None = None,
    index: int | None = None,
    enabled: bool | None = None,
    confirm: bool = False,
) -> str:
    """Add an APT repository (elevated, confirm required)."""
    return apt.add_apt_repo(client, node=node, path=path, index=index, enabled=enabled, confirm=confirm)


@mcp.tool()
def proxmox_update_apt_repo(
    node: str | None = None,
    path: str | None = None,
    index: int | None = None,
    enabled: bool | None = None,
    confirm: bool = False,
) -> str:
    """Update an APT repository (elevated, confirm required)."""
    return apt.update_apt_repo(client, node=node, path=path, index=index, enabled=enabled, confirm=confirm)


@mcp.tool()
def proxmox_list_apt_changelog(
    node: str | None = None,
    name: str | None = None,
    version: str | None = None,
) -> str:
    """List APT changelog for a package (read-only)."""
    return apt.list_apt_changelog(client, node=node, name=name, version=version)


@mcp.tool()
def proxmox_list_cpu_models(node: str | None = None) -> str:
    """List QEMU CPU models on a node (read-only)."""
    return capabilities.list_cpu_models(client, node=node)


@mcp.tool()
def proxmox_list_cpu_flags(node: str | None = None) -> str:
    """List QEMU CPU flags on a node (read-only)."""
    return capabilities.list_cpu_flags(client, node=node)


@mcp.tool()
def proxmox_list_machine_types(node: str | None = None) -> str:
    """List QEMU machine types on a node (read-only)."""
    return capabilities.list_machine_types(client, node=node)


@mcp.tool()
def proxmox_list_capabilities(node: str | None = None) -> str:
    """List node capabilities index (read-only)."""
    return capabilities.list_capabilities(client, node=node)


@mcp.tool()
def proxmox_list_capabilities_qemu(node: str | None = None) -> str:
    """List QEMU capabilities on a node (read-only)."""
    return capabilities.list_capabilities_qemu(client, node=node)


@mcp.tool()
def proxmox_get_capability_qemu_migration(node: str | None = None) -> str:
    """Get QEMU migration capabilities on a node (read-only)."""
    return capabilities.get_capability_qemu_migrations(client, node=node)


@mcp.tool()
def proxmox_list_certificates(node: str | None = None) -> str:
    """List certificate info on a node (read-only)."""
    return certificates.list_certificates(client, node=node)


@mcp.tool()
def proxmox_order_acme_certificate(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Order ACME certificate (elevated, confirm required)."""
    return certificates.order_acme_certificate(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_renew_acme_certificate(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Renew ACME certificate (elevated, confirm required)."""
    return certificates.renew_acme_certificate(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_revoke_certificate(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Revoke certificate from ACME CA (elevated, confirm required)."""
    return certificates.revoke_certificate(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_upload_custom_certificate(
    node: str | None = None,
    certificates: str | None = None,
    key: str | None = None,
    confirm: bool = False,
) -> str:
    """Upload custom certificate and key (elevated, confirm required)."""
    return certificates.upload_custom_certificate(
        client, node=node, certificates=certificates, key=key, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_custom_certificate(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Delete custom certificate (elevated, confirm required)."""
    return certificates.delete_custom_certificate(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_list_acme_certs(node: str | None = None) -> str:
    """List ACME certificate entries on a node (read-only)."""
    return certificates.list_acme_certs(client, node=node)


@mcp.tool()
def proxmox_list_sdn_zones() -> str:
    """List SDN zones in the cluster (read-only)."""
    return sdn.list_sdn_zones(client)


@mcp.tool()
def proxmox_get_sdn_zone(zone: str = "") -> str:
    """Get SDN zone configuration (read-only)."""
    return sdn.get_sdn_zone(client, zone=zone)


@mcp.tool()
def proxmox_create_sdn_zone(
    zone: str = "",
    type: str = "",
    comment: str | None = None,
    nodes: str | None = None,
    confirm: bool = False,
) -> str:
    """Create an SDN zone (elevated, confirm required)."""
    return sdn.create_sdn_zone(
        client, zone=zone, type=type, comment=comment, nodes=nodes, confirm=confirm,
    )


@mcp.tool()
def proxmox_update_sdn_zone(
    zone: str = "",
    comment: str | None = None,
    nodes: str | None = None,
    confirm: bool = False,
) -> str:
    """Update an SDN zone (elevated, confirm required)."""
    return sdn.update_sdn_zone(client, zone=zone, comment=comment, nodes=nodes, confirm=confirm)


@mcp.tool()
def proxmox_delete_sdn_zone(
    zone: str = "",
    confirm: bool = False,
) -> str:
    """Delete an SDN zone (elevated, confirm required)."""
    return sdn.delete_sdn_zone(client, zone=zone, confirm=confirm)


@mcp.tool()
def proxmox_list_sdn_vnets() -> str:
    """List SDN VNets in the cluster (read-only)."""
    return sdn.list_sdn_vnets(client)


@mcp.tool()
def proxmox_get_sdn_vnet(vnet: str = "") -> str:
    """Get SDN VNet configuration (read-only)."""
    return sdn.get_sdn_vnet(client, vnet=vnet)


@mcp.tool()
def proxmox_create_sdn_vnet(
    vnet: str = "",
    zone: str = "",
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create an SDN VNet (elevated, confirm required)."""
    return sdn.create_sdn_vnet(
        client, vnet=vnet, zone=zone, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_update_sdn_vnet(
    vnet: str = "",
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Update an SDN VNet (elevated, confirm required)."""
    return sdn.update_sdn_vnet(client, vnet=vnet, comment=comment, confirm=confirm)


@mcp.tool()
def proxmox_delete_sdn_vnet(
    vnet: str = "",
    confirm: bool = False,
) -> str:
    """Delete an SDN VNet (elevated, confirm required)."""
    return sdn.delete_sdn_vnet(client, vnet=vnet, confirm=confirm)


@mcp.tool()
def proxmox_list_sdn_subnets(vnet: str = "") -> str:
    """List SDN subnets in a VNet (read-only)."""
    return sdn.list_sdn_subnets(client, vnet=vnet)


@mcp.tool()
def proxmox_create_sdn_subnet(
    vnet: str = "",
    subnet: str = "",
    confirm: bool = False,
) -> str:
    """Create an SDN subnet (elevated, confirm required)."""
    return sdn.create_sdn_subnet(client, vnet=vnet, subnet=subnet, confirm=confirm)


@mcp.tool()
def proxmox_delete_sdn_subnet(
    vnet: str = "",
    subnet: str = "",
    confirm: bool = False,
) -> str:
    """Delete an SDN subnet (elevated, confirm required)."""
    return sdn.delete_sdn_subnet(client, vnet=vnet, subnet=subnet, confirm=confirm)


@mcp.tool()
def proxmox_list_sdn_controllers() -> str:
    """List SDN controllers in the cluster (read-only)."""
    return sdn.list_sdn_controllers(client)


@mcp.tool()
def proxmox_create_sdn_controller(
    controller: str = "",
    type: str = "",
    confirm: bool = False,
) -> str:
    """Create an SDN controller (elevated, confirm required)."""
    return sdn.create_sdn_controller(client, controller=controller, type=type, confirm=confirm)


@mcp.tool()
def proxmox_delete_sdn_controller(
    controller: str = "",
    confirm: bool = False,
) -> str:
    """Delete an SDN controller (elevated, confirm required)."""
    return sdn.delete_sdn_controller(client, controller=controller, confirm=confirm)


@mcp.tool()
def proxmox_list_sdn_dns() -> str:
    """List SDN DNS entries in the cluster (read-only)."""
    return sdn.list_sdn_dns(client)


@mcp.tool()
def proxmox_create_sdn_dns(
    dns: str = "",
    type: str = "",
    confirm: bool = False,
) -> str:
    """Create an SDN DNS entry (elevated, confirm required)."""
    return sdn.create_sdn_dns(client, dns=dns, type=type, confirm=confirm)


@mcp.tool()
def proxmox_delete_sdn_dns(
    dns: str = "",
    confirm: bool = False,
) -> str:
    """Delete an SDN DNS entry (elevated, confirm required)."""
    return sdn.delete_sdn_dns(client, dns=dns, confirm=confirm)


@mcp.tool()
def proxmox_list_sdn_ipams() -> str:
    """List SDN IPAMs in the cluster (read-only)."""
    return sdn.list_sdn_ipams(client)


@mcp.tool()
def proxmox_create_sdn_ipam(
    ipam: str = "",
    type: str = "",
    confirm: bool = False,
) -> str:
    """Create an SDN IPAM (elevated, confirm required)."""
    return sdn.create_sdn_ipam(client, ipam=ipam, type=type, confirm=confirm)


@mcp.tool()
def proxmox_delete_sdn_ipam(
    ipam: str = "",
    confirm: bool = False,
) -> str:
    """Delete an SDN IPAM (elevated, confirm required)."""
    return sdn.delete_sdn_ipam(client, ipam=ipam, confirm=confirm)


@mcp.tool()
def proxmox_apply_sdn(confirm: bool = False) -> str:
    """Apply pending SDN changes (elevated, confirm required)."""
    return sdn.apply_sdn(client, confirm=confirm)


@mcp.tool()
def proxmox_list_node_sdn_zones(node: str | None = None) -> str:
    """List SDN zone status on a node (read-only)."""
    return sdn.list_node_sdn_zones(client, node=node)


@mcp.tool()
def proxmox_get_node_sdn_zone_status(node: str | None = None, zone: str = "") -> str:
    """Get SDN zone status on a node (read-only)."""
    return sdn.get_node_sdn_zone_status(client, node=node, zone=zone)


@mcp.tool()
def proxmox_list_notification_targets() -> str:
    """List notification targets (read-only)."""
    return notifications.list_notification_targets(client)


@mcp.tool()
def proxmox_list_notification_matchers() -> str:
    """List notification matchers (read-only)."""
    return notifications.list_notification_matchers(client)


@mcp.tool()
def proxmox_get_notification_matcher(name: str = "") -> str:
    """Get notification matcher configuration (read-only)."""
    return notifications.get_notification_matcher(client, name=name)


@mcp.tool()
def proxmox_list_sendmail_endpoints() -> str:
    """List sendmail notification endpoints (read-only)."""
    return notifications.list_sendmail_endpoints(client)


@mcp.tool()
def proxmox_create_sendmail_endpoint(
    name: str = "",
    mailto: str | None = None,
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a sendmail notification endpoint (elevated, confirm required)."""
    return notifications.create_sendmail_endpoint(
        client, name=name, mailto=mailto, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_sendmail_endpoint(
    name: str = "",
    confirm: bool = False,
) -> str:
    """Delete a sendmail notification endpoint (elevated, confirm required)."""
    return notifications.delete_sendmail_endpoint(client, name=name, confirm=confirm)


@mcp.tool()
def proxmox_list_smtp_endpoints() -> str:
    """List SMTP notification endpoints (read-only)."""
    return notifications.list_smtp_endpoints(client)


@mcp.tool()
def proxmox_create_smtp_endpoint(
    name: str = "",
    server: str | None = None,
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create an SMTP notification endpoint (elevated, confirm required)."""
    return notifications.create_smtp_endpoint(
        client, name=name, server=server, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_smtp_endpoint(
    name: str = "",
    confirm: bool = False,
) -> str:
    """Delete an SMTP notification endpoint (elevated, confirm required)."""
    return notifications.delete_smtp_endpoint(client, name=name, confirm=confirm)


@mcp.tool()
def proxmox_list_gotify_endpoints() -> str:
    """List Gotify notification endpoints (read-only)."""
    return notifications.list_gotify_endpoints(client)


@mcp.tool()
def proxmox_create_gotify_endpoint(
    name: str = "",
    server: str | None = None,
    token: str | None = None,
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a Gotify notification endpoint (elevated, confirm required)."""
    return notifications.create_gotify_endpoint(
        client, name=name, server=server, token=token, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_gotify_endpoint(
    name: str = "",
    confirm: bool = False,
) -> str:
    """Delete a Gotify notification endpoint (elevated, confirm required)."""
    return notifications.delete_gotify_endpoint(client, name=name, confirm=confirm)


@mcp.tool()
def proxmox_list_webhook_endpoints() -> str:
    """List webhook notification endpoints (read-only)."""
    return notifications.list_webhook_endpoints(client)


@mcp.tool()
def proxmox_create_webhook_endpoint(
    name: str = "",
    url: str | None = None,
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a webhook notification endpoint (elevated, confirm required)."""
    return notifications.create_webhook_endpoint(
        client, name=name, url=url, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_webhook_endpoint(
    name: str = "",
    confirm: bool = False,
) -> str:
    """Delete a webhook notification endpoint (elevated, confirm required)."""
    return notifications.delete_webhook_endpoint(client, name=name, confirm=confirm)


@mcp.tool()
def proxmox_notification_index() -> str:
    """Get notification system index (read-only)."""
    return notifications.notification_index(client)


@mcp.tool()
def proxmox_notification_endpoints_index() -> str:
    """Get notification endpoints index (read-only)."""
    return notifications.notification_endpoints_index(client)


@mcp.tool()
def proxmox_get_notification_target(name: str = "") -> str:
    """Get notification target details (read-only)."""
    return notifications.get_notification_target(client, name=name)


@mcp.tool()
def proxmox_test_notification_target(
    name: str = "",
    confirm: bool = False,
) -> str:
    """Send a test notification to a target (elevated, confirm required)."""
    return notifications.test_notification_target(client, name=name, confirm=confirm)


@mcp.tool()
def proxmox_notification_matcher_fields() -> str:
    """List notification matcher fields (read-only)."""
    return notifications.notification_matcher_fields(client)


@mcp.tool()
def proxmox_notification_matcher_field_values() -> str:
    """List notification matcher field values (read-only)."""
    return notifications.notification_matcher_field_values(client)


@mcp.tool()
def proxmox_create_notification_matcher(
    name: str = "",
    comment: str | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Create a notification matcher (elevated, confirm required)."""
    return notifications.create_notification_matcher(client, name=name, comment=comment, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_update_notification_matcher(
    name: str = "",
    comment: str | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update a notification matcher (elevated, confirm required)."""
    return notifications.update_notification_matcher(client, name=name, comment=comment, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_delete_notification_matcher(
    name: str = "",
    confirm: bool = False,
) -> str:
    """Delete a notification matcher (elevated, confirm required)."""
    return notifications.delete_notification_matcher(client, name=name, confirm=confirm)


@mcp.tool()
def proxmox_get_sendmail_endpoint(name: str = "") -> str:
    """Get sendmail endpoint details (read-only)."""
    return notifications.get_sendmail_endpoint(client, name=name)


@mcp.tool()
def proxmox_update_sendmail_endpoint(
    name: str = "",
    comment: str | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update a sendmail endpoint (elevated, confirm required)."""
    return notifications.update_sendmail_endpoint(client, name=name, comment=comment, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_get_smtp_endpoint(name: str = "") -> str:
    """Get SMTP endpoint details (read-only)."""
    return notifications.get_smtp_endpoint(client, name=name)


@mcp.tool()
def proxmox_update_smtp_endpoint(
    name: str = "",
    comment: str | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update an SMTP endpoint (elevated, confirm required)."""
    return notifications.update_smtp_endpoint(client, name=name, comment=comment, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_get_gotify_endpoint(name: str = "") -> str:
    """Get Gotify endpoint details (read-only)."""
    return notifications.get_gotify_endpoint(client, name=name)


@mcp.tool()
def proxmox_update_gotify_endpoint(
    name: str = "",
    comment: str | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update a Gotify endpoint (elevated, confirm required)."""
    return notifications.update_gotify_endpoint(client, name=name, comment=comment, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_get_webhook_endpoint(name: str = "") -> str:
    """Get webhook endpoint details (read-only)."""
    return notifications.get_webhook_endpoint(client, name=name)


@mcp.tool()
def proxmox_update_webhook_endpoint(
    name: str = "",
    comment: str | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update a webhook endpoint (elevated, confirm required)."""
    return notifications.update_webhook_endpoint(client, name=name, comment=comment, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_list_pci_mappings() -> str:
    """List PCI hardware mappings (read-only)."""
    return mapping.list_pci_mappings(client)


@mcp.tool()
def proxmox_create_pci_mapping(
    id: str = "",
    description: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a PCI hardware mapping (elevated, confirm required)."""
    return mapping.create_pci_mapping(client, id=id, description=description, confirm=confirm)


@mcp.tool()
def proxmox_get_pci_mapping(id: str = "") -> str:
    """Get PCI hardware mapping configuration (read-only)."""
    return mapping.get_pci_mapping(client, id=id)


@mcp.tool()
def proxmox_update_pci_mapping(
    id: str = "",
    description: str | None = None,
    confirm: bool = False,
) -> str:
    """Update a PCI hardware mapping (elevated, confirm required)."""
    return mapping.update_pci_mapping(client, id=id, description=description, confirm=confirm)


@mcp.tool()
def proxmox_delete_pci_mapping(
    id: str = "",
    confirm: bool = False,
) -> str:
    """Delete a PCI hardware mapping (elevated, confirm required)."""
    return mapping.delete_pci_mapping(client, id=id, confirm=confirm)


@mcp.tool()
def proxmox_list_usb_mappings() -> str:
    """List USB hardware mappings (read-only)."""
    return mapping.list_usb_mappings(client)


@mcp.tool()
def proxmox_create_usb_mapping(
    id: str = "",
    description: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a USB hardware mapping (elevated, confirm required)."""
    return mapping.create_usb_mapping(client, id=id, description=description, confirm=confirm)


@mcp.tool()
def proxmox_get_usb_mapping(id: str = "") -> str:
    """Get USB hardware mapping configuration (read-only)."""
    return mapping.get_usb_mapping(client, id=id)


@mcp.tool()
def proxmox_update_usb_mapping(
    id: str = "",
    description: str | None = None,
    confirm: bool = False,
) -> str:
    """Update a USB hardware mapping (elevated, confirm required)."""
    return mapping.update_usb_mapping(client, id=id, description=description, confirm=confirm)


@mcp.tool()
def proxmox_delete_usb_mapping(
    id: str = "",
    confirm: bool = False,
) -> str:
    """Delete a USB hardware mapping (elevated, confirm required)."""
    return mapping.delete_usb_mapping(client, id=id, confirm=confirm)


@mcp.tool()
def proxmox_mapping_index() -> str:
    """Get mapping resource types index (read-only)."""
    return mapping.mapping_index(client)


@mcp.tool()
def proxmox_list_dir_mappings() -> str:
    """List directory mappings (read-only)."""
    return mapping.list_dir_mappings(client)


@mcp.tool()
def proxmox_get_dir_mapping(id: str = "") -> str:
    """Get directory mapping configuration (read-only)."""
    return mapping.get_dir_mapping(client, id=id)


@mcp.tool()
def proxmox_create_dir_mapping(
    id: str = "",
    description: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a directory mapping (elevated, confirm required)."""
    return mapping.create_dir_mapping(client, id=id, description=description, confirm=confirm)


@mcp.tool()
def proxmox_update_dir_mapping(
    id: str = "",
    description: str | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update a directory mapping (elevated, confirm required)."""
    return mapping.update_dir_mapping(client, id=id, description=description, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_delete_dir_mapping(
    id: str = "",
    confirm: bool = False,
) -> str:
    """Delete a directory mapping (elevated, confirm required)."""
    return mapping.delete_dir_mapping(client, id=id, confirm=confirm)


@mcp.tool()
def proxmox_list_metric_servers() -> str:
    """List metric server configurations (read-only)."""
    return metrics.list_metric_servers(client)


@mcp.tool()
def proxmox_get_metric_server(id: str = "") -> str:
    """Get metric server configuration (read-only)."""
    return metrics.get_metric_server(client, id=id)


@mcp.tool()
def proxmox_create_metric_server(
    id: str = "",
    type: str = "graphite",
    server: str | None = None,
    port: int | None = None,
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create a metric server configuration (elevated, confirm required). type: graphite, influxdb, opentelemetry."""
    return metrics.create_metric_server(
        client, id=id, type=type, server=server, port=port, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_update_metric_server(
    id: str = "",
    server: str | None = None,
    port: int | None = None,
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Update a metric server configuration (elevated, confirm required)."""
    return metrics.update_metric_server(
        client, id=id, server=server, port=port, comment=comment, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_metric_server(
    id: str = "",
    confirm: bool = False,
) -> str:
    """Delete a metric server configuration (elevated, confirm required)."""
    return metrics.delete_metric_server(client, id=id, confirm=confirm)


@mcp.tool()
def proxmox_metrics_index() -> str:
    """Get metrics subsystem index (read-only)."""
    return metrics.metrics_index(client)


@mcp.tool()
def proxmox_export_metrics() -> str:
    """Export cluster metrics data (read-only)."""
    return metrics.export_metrics(client)


@mcp.tool()
def proxmox_node_netstat(node: str | None = None) -> str:
    """Get network device interface counters for a node (read-only)."""
    return nodes.node_netstat(client, node=node)


@mcp.tool()
def proxmox_lxc_migrate_preconditions(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Check LXC container migration preconditions (read-only)."""
    return lifecycle.lxc_migrate_preconditions(client, node=node, vmid=vmid)


@mcp.tool()
def proxmox_vm_migrate_preconditions(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Check VM migration preconditions (read-only)."""
    return lifecycle.vm_migrate_preconditions(client, node=node, vmid=vmid)


@mcp.tool()
def proxmox_storage_metrics(
    node: str | None = None,
    storage: str = "local",
    timeframe: str = "hour",
    cf: str = "AVERAGE",
) -> str:
    """Get RRD metrics for a storage pool on a node (read-only)."""
    return storage_mod.storage_metrics(client, node=node, storage=storage, timeframe=timeframe, cf=cf)


@mcp.tool()
def proxmox_storage_identity(
    node: str | None = None,
    storage: str = "local",
) -> str:
    """Get storage identity information (read-only)."""
    return storage_mod.storage_identity(client, node=node, storage=storage)


@mcp.tool()
def proxmox_allocate_disk(
    node: str | None = None,
    storage: str = "local",
    vmid: int | None = None,
    filename: str | None = None,
    size: str = "1G",
    format: str | None = None,
    confirm: bool = False,
) -> str:
    """Allocate a disk image on storage (elevated, confirm required)."""
    return storage_mod.allocate_disk(
        client, node=node, storage=storage, vmid=vmid,
        filename=filename, size=size, format=format, confirm=confirm,
    )


@mcp.tool()
def proxmox_list_node_lxc(node: str | None = None) -> str:
    """List LXC containers on a specific node (read-only)."""
    return discovery.list_node_lxc(client, node=node)


@mcp.tool()
def proxmox_list_node_vms(node: str | None = None) -> str:
    """List VMs on a specific node (read-only)."""
    return discovery.list_node_vms(client, node=node)


@mcp.tool()
def proxmox_list_node_tasks(node: str | None = None, limit: int = 50) -> str:
    """List tasks on a specific node (read-only)."""
    return discovery.list_node_tasks(client, node=node, limit=limit)


@mcp.tool()
def proxmox_node_index(node: str | None = None) -> str:
    """Get node index information (read-only)."""
    return discovery.node_index(client, node=node)


@mcp.tool()
def proxmox_regenerate_cloudinit(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = False,
) -> str:
    """Regenerate cloud-init drive for a VM (elevated, confirm required)."""
    return cloudinit.regenerate_cloudinit(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_revert_network(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Revert pending network changes on a node (elevated, confirm required)."""
    return networking.revert_network(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_get_acme_challenge_schema() -> str:
    """Get ACME challenge schema (read-only)."""
    return acme.get_acme_challenge_schema(client)


@mcp.tool()
def proxmox_list_acme_tos() -> str:
    """List ACME Terms of Service (read-only, deprecated)."""
    return acme.list_acme_tos(client)


@mcp.tool()
def proxmox_get_sdn_ipam_status(ipam: str = "") -> str:
    """Get SDN IPAM status (read-only)."""
    return sdn.get_sdn_ipam_status(client, ipam=ipam)


@mcp.tool()
def proxmox_list_sdn_fabrics() -> str:
    """List SDN fabrics (read-only)."""
    return sdn.list_sdn_fabrics(client)


@mcp.tool()
def proxmox_list_sdn_fabric_detail(fabric: str = "") -> str:
    """Get SDN fabric detail (read-only)."""
    return sdn.list_sdn_fabric_detail(client, fabric=fabric)


@mcp.tool()
def proxmox_create_sdn_fabric(
    fabric: str = "",
    type: str = "",
    confirm: bool = False,
) -> str:
    """Create an SDN fabric (elevated, confirm required)."""
    return sdn.create_sdn_fabric(client, fabric=fabric, type=type, confirm=confirm)


@mcp.tool()
def proxmox_delete_sdn_fabric(
    id: str = "",
    confirm: bool = False,
) -> str:
    """Delete an SDN fabric (elevated, confirm required)."""
    return sdn.delete_sdn_fabric(client, id=id, confirm=confirm)


@mcp.tool()
def proxmox_update_sdn_fabric(
    id: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update an SDN fabric (elevated, confirm required)."""
    return sdn.update_sdn_fabric(client, id=id, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_list_sdn_prefix_lists() -> str:
    """List SDN prefix lists (read-only)."""
    return sdn.list_sdn_prefix_lists(client)


@mcp.tool()
def proxmox_create_sdn_prefix_list(
    id: str = "",
    confirm: bool = False,
) -> str:
    """Create an SDN prefix list (elevated, confirm required)."""
    return sdn.create_sdn_prefix_list(client, id=id, confirm=confirm)


@mcp.tool()
def proxmox_delete_sdn_prefix_list(
    id: str = "",
    confirm: bool = False,
) -> str:
    """Delete an SDN prefix list (elevated, confirm required)."""
    return sdn.delete_sdn_prefix_list(client, id=id, confirm=confirm)


@mcp.tool()
def proxmox_list_sdn_route_maps() -> str:
    """List SDN route maps (read-only)."""
    return sdn.list_sdn_route_maps(client)


@mcp.tool()
def proxmox_sdn_rollback(confirm: bool = False) -> str:
    """Rollback pending SDN changes (elevated, confirm required)."""
    return sdn.sdn_rollback(client, confirm=confirm)


@mcp.tool()
def proxmox_get_sdn_ipam(ipam: str = "") -> str:
    """Get SDN IPAM configuration (read-only)."""
    return sdn.get_sdn_ipam(client, ipam=ipam)


@mcp.tool()
def proxmox_update_sdn_ipam(
    ipam: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update an SDN IPAM (elevated, confirm required)."""
    return sdn.update_sdn_ipam(client, ipam=ipam, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_get_sdn_dns(dns: str = "") -> str:
    """Get SDN DNS configuration (read-only)."""
    return sdn.get_sdn_dns(client, dns=dns)


@mcp.tool()
def proxmox_update_sdn_dns(
    dns: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update an SDN DNS entry (elevated, confirm required)."""
    return sdn.update_sdn_dns(client, dns=dns, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_get_sdn_controller(controller: str = "") -> str:
    """Get SDN controller configuration (read-only)."""
    return sdn.get_sdn_controller(client, controller=controller)


@mcp.tool()
def proxmox_update_sdn_controller(
    controller: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update an SDN controller (elevated, confirm required)."""
    return sdn.update_sdn_controller(client, controller=controller, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_list_sdn_fabric_nodes(fabric_id: str = "") -> str:
    """List SDN fabric nodes (read-only)."""
    return sdn.list_sdn_fabric_nodes(client, fabric_id=fabric_id)


@mcp.tool()
def proxmox_add_sdn_fabric_node(
    fabric_id: str = "",
    node: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Add an SDN fabric node (elevated, confirm required)."""
    return sdn.add_sdn_fabric_node(client, fabric_id=fabric_id, node=node, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_get_sdn_fabric_node(fabric_id: str = "", node_id: str = "") -> str:
    """Get SDN fabric node detail (read-only)."""
    return sdn.get_sdn_fabric_node(client, fabric_id=fabric_id, node_id=node_id)


@mcp.tool()
def proxmox_update_sdn_fabric_node(
    fabric_id: str = "",
    node_id: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update an SDN fabric node (elevated, confirm required)."""
    return sdn.update_sdn_fabric_node(client, fabric_id=fabric_id, node_id=node_id, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_remove_sdn_fabric_node(
    fabric_id: str = "",
    node_id: str = "",
    confirm: bool = False,
) -> str:
    """Remove an SDN fabric node (elevated, confirm required)."""
    return sdn.remove_sdn_fabric_node(client, fabric_id=fabric_id, node_id=node_id, confirm=confirm)


@mcp.tool()
def proxmox_create_sdn_vnet_ip(
    vnet: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Create an SDN VNet IP mapping (elevated, confirm required)."""
    return sdn.create_sdn_vnet_ip(client, vnet=vnet, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_update_sdn_vnet_ip(
    vnet: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update an SDN VNet IP mapping (elevated, confirm required)."""
    return sdn.update_sdn_vnet_ip(client, vnet=vnet, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_delete_sdn_vnet_ip(
    vnet: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Delete an SDN VNet IP mapping (elevated, confirm required)."""
    return sdn.delete_sdn_vnet_ip(client, vnet=vnet, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_get_sdn_vnet_firewall_options(vnet: str = "") -> str:
    """Get SDN VNet firewall options (read-only)."""
    return sdn.get_sdn_vnet_firewall_options(client, vnet=vnet)


@mcp.tool()
def proxmox_set_sdn_vnet_firewall_options(
    vnet: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Set SDN VNet firewall options (elevated, confirm required)."""
    return sdn.set_sdn_vnet_firewall_options(client, vnet=vnet, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_list_sdn_vnet_firewall_rules(vnet: str = "") -> str:
    """List SDN VNet firewall rules (read-only)."""
    return sdn.list_sdn_vnet_firewall_rules(client, vnet=vnet)


@mcp.tool()
def proxmox_create_sdn_vnet_firewall_rule(
    vnet: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Create an SDN VNet firewall rule (elevated, confirm required)."""
    return sdn.create_sdn_vnet_firewall_rule(client, vnet=vnet, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_delete_sdn_vnet_firewall_rule(
    vnet: str = "",
    pos: int = 0,
    confirm: bool = False,
) -> str:
    """Delete an SDN VNet firewall rule (elevated, confirm required)."""
    return sdn.delete_sdn_vnet_firewall_rule(client, vnet=vnet, pos=pos, confirm=confirm)


@mcp.tool()
def proxmox_get_sdn_vnet_firewall_rule(vnet: str = "", pos: int = 0) -> str:
    """Get an SDN VNet firewall rule (read-only)."""
    return sdn.get_sdn_vnet_firewall_rule(client, vnet=vnet, pos=pos)


@mcp.tool()
def proxmox_update_sdn_vnet_firewall_rule(
    vnet: str = "",
    pos: int = 0,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update an SDN VNet firewall rule (elevated, confirm required)."""
    return sdn.update_sdn_vnet_firewall_rule(client, vnet=vnet, pos=pos, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_list_prefix_list_entries(id: str = "") -> str:
    """List SDN prefix list entries (read-only)."""
    return sdn.list_prefix_list_entries(client, id=id)


@mcp.tool()
def proxmox_create_prefix_list_entry(
    id: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Create an SDN prefix list entry (elevated, confirm required)."""
    return sdn.create_prefix_list_entry(client, id=id, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_delete_prefix_list_entry(
    id: str = "",
    url_seq: int = 0,
    confirm: bool = False,
) -> str:
    """Delete an SDN prefix list entry (elevated, confirm required)."""
    return sdn.delete_prefix_list_entry(client, id=id, url_seq=url_seq, confirm=confirm)


@mcp.tool()
def proxmox_get_prefix_list_entry(id: str = "", url_seq: int = 0) -> str:
    """Get an SDN prefix list entry (read-only)."""
    return sdn.get_prefix_list_entry(client, id=id, url_seq=url_seq)


@mcp.tool()
def proxmox_update_prefix_list_entry(
    id: str = "",
    url_seq: int = 0,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update an SDN prefix list entry (elevated, confirm required)."""
    return sdn.update_prefix_list_entry(client, id=id, url_seq=url_seq, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_list_route_map_entries() -> str:
    """List SDN route map entries (read-only)."""
    return sdn.list_route_map_entries(client)


@mcp.tool()
def proxmox_create_route_map_entry(
    route_map_id: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Create an SDN route map entry (elevated, confirm required)."""
    return sdn.create_route_map_entry(client, route_map_id=route_map_id, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_get_route_map_entry(route_map_id: str = "") -> str:
    """Get SDN route map entry detail (read-only)."""
    return sdn.get_route_map_entry(client, route_map_id=route_map_id)


@mcp.tool()
def proxmox_delete_route_map_entry(
    route_map_id: str = "",
    order: int = 0,
    confirm: bool = False,
) -> str:
    """Delete an SDN route map entry (elevated, confirm required)."""
    return sdn.delete_route_map_entry(client, route_map_id=route_map_id, order=order, confirm=confirm)


@mcp.tool()
def proxmox_update_route_map_entry(
    route_map_id: str = "",
    order: int = 0,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update an SDN route map entry (elevated, confirm required)."""
    return sdn.update_route_map_entry(client, route_map_id=route_map_id, order=order, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_sdn_dry_run() -> str:
    """Preview pending SDN changes (read-only dry-run)."""
    return sdn.sdn_dry_run(client)


@mcp.tool()
def proxmox_get_node_sdn_vnet(node: str | None = None, vnet: str = "") -> str:
    """Get SDN VNet status on a node (read-only)."""
    return sdn.get_node_sdn_vnet(client, node=node, vnet=vnet)


@mcp.tool()
def proxmox_list_node_sdn_zone_bridges(node: str | None = None, zone: str = "") -> str:
    """List SDN zone bridges on a node (read-only)."""
    return sdn.list_node_sdn_zone_bridges(client, node=node, zone=zone)


@mcp.tool()
def proxmox_get_node_sdn_zone_content(node: str | None = None, zone: str = "") -> str:
    """Get SDN zone content on a node (read-only)."""
    return sdn.get_node_sdn_zone_content(client, node=node, zone=zone)


@mcp.tool()
def proxmox_get_node_sdn_zone_ip_vrf(node: str | None = None, zone: str = "") -> str:
    """Get SDN zone IP-VRF on a node (read-only)."""
    return sdn.get_node_sdn_zone_ip_vrf(client, node=node, zone=zone)


@mcp.tool()
def proxmox_send_vm_key(
    node: str | None = None,
    vmid: int | None = None,
    key: str = "",
    confirm: bool = False,
) -> str:
    """Send a key press to a VM (elevated, confirm required)."""
    return lifecycle.send_vm_key(client, node=node, vmid=vmid, key=key, confirm=confirm)


@mcp.tool()
def proxmox_vm_monitor_command(
    node: str | None = None,
    vmid: int | None = None,
    command: str = "",
    confirm: bool = False,
) -> str:
    """Send raw QEMU monitor command to VM (elevated, confirm required, VERY DANGEROUS)."""
    return lifecycle.vm_monitor_command(client, node=node, vmid=vmid, command=command, confirm=confirm)


@mcp.tool()
def proxmox_unlink_vm_disk(
    node: str | None = None,
    vmid: int | None = None,
    idlist: str = "",
    confirm: bool = False,
) -> str:
    """Unlink disks from a VM (elevated, confirm required). idlist is comma-separated disk IDs."""
    return lifecycle.unlink_vm_disk(client, node=node, vmid=vmid, idlist=idlist, confirm=confirm)


@mcp.tool()
def proxmox_vm_dbus_vmstate(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = False,
) -> str:
    """Trigger DBus VMstate save on a VM (elevated, confirm required)."""
    return lifecycle.vm_dbus_vmstate(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_bulk_start_guests(
    vmids: str = "",
    confirm: bool = False,
) -> str:
    """Bulk start guests across the cluster (elevated, confirm required)."""
    return cluster.bulk_start_guests(client, vmids=vmids, confirm=confirm)


@mcp.tool()
def proxmox_bulk_suspend_guests(
    vmids: str = "",
    confirm: bool = False,
) -> str:
    """Bulk suspend guests across the cluster (elevated, confirm required)."""
    return cluster.bulk_suspend_guests(client, vmids=vmids, confirm=confirm)


@mcp.tool()
def proxmox_vm_vnc_proxy(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = False,
) -> str:
    """Create VNC proxy for a VM (elevated, confirm required)."""
    return console.vm_vnc_proxy(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_vm_spice_proxy(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = False,
) -> str:
    """Create SPICE proxy for a VM (elevated, confirm required)."""
    return console.vm_spice_proxy(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_vm_termproxy(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = False,
) -> str:
    """Create terminal proxy for a VM (elevated, confirm required)."""
    return console.vm_termproxy(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_lxc_vnc_proxy(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = False,
) -> str:
    """Create VNC proxy for an LXC container (elevated, confirm required)."""
    return console.lxc_vnc_proxy(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_lxc_termproxy(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = False,
) -> str:
    """Create terminal proxy for an LXC container (elevated, confirm required)."""
    return console.lxc_termproxy(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_lxc_spice_proxy(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = False,
) -> str:
    """Create SPICE proxy for an LXC container (elevated, confirm required)."""
    return console.lxc_spice_proxy(client, node=node, vmid=vmid, confirm=confirm)


@mcp.tool()
def proxmox_lxc_vnc_websocket(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get VNC websocket info for an LXC container (read-only)."""
    return console.lxc_vnc_websocket(client, node=node, vmid=vmid)


@mcp.tool()
def proxmox_node_vncshell(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Create VNC shell for a node (elevated, confirm required)."""
    return console.node_vncshell(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_node_spiceshell(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Create SPICE shell for a node (elevated, confirm required)."""
    return console.node_spiceshell(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_node_termproxy(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Create terminal proxy for a node (elevated, confirm required)."""
    return console.node_termproxy(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_list_tfa() -> str:
    """List TFA configurations (read-only)."""
    return access.list_tfa(client)


@mcp.tool()
def proxmox_get_user_tfa(userid: str = "") -> str:
    """Get TFA entries for a user (read-only)."""
    return access.get_user_tfa(client, userid=userid)


@mcp.tool()
def proxmox_add_tfa_entry(
    userid: str = "",
    type: str = "",
    description: str | None = None,
    value: str | None = None,
    confirm: bool = False,
) -> str:
    """Add a TFA entry for a user (elevated, confirm required)."""
    return access.add_tfa_entry(
        client, userid=userid, type=type, description=description,
        value=value, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_tfa_entry(
    userid: str = "",
    id: str = "",
    confirm: bool = False,
) -> str:
    """Delete a TFA entry (elevated, confirm required)."""
    return access.delete_tfa_entry(client, userid=userid, id=id, confirm=confirm)


@mcp.tool()
def proxmox_get_tfa_entry(userid: str = "", id: str = "") -> str:
    """Get a specific TFA entry (read-only)."""
    return access.get_tfa_entry(client, userid=userid, id=id)


@mcp.tool()
def proxmox_update_tfa_entry(
    userid: str = "",
    id: str = "",
    description: str | None = None,
    enable: bool | None = None,
    confirm: bool = False,
) -> str:
    """Update a TFA entry (elevated, confirm required)."""
    return access.update_tfa_entry(
        client, userid=userid, id=id, description=description,
        enable=enable, confirm=confirm,
    )


@mcp.tool()
def proxmox_unlock_tfa(
    userid: str = "",
    confirm: bool = False,
) -> str:
    """Unlock a user's TFA authentication (elevated, confirm required)."""
    return access.unlock_tfa(client, userid=userid, confirm=confirm)


@mcp.tool()
def proxmox_list_domains() -> str:
    """List authentication domains (read-only)."""
    return access.list_domains(client)


@mcp.tool()
def proxmox_get_domain(realm: str = "") -> str:
    """Get auth domain configuration (read-only)."""
    return access.get_domain(client, realm=realm)


@mcp.tool()
def proxmox_sync_domain(
    realm: str = "",
    confirm: bool = False,
) -> str:
    """Sync users/groups from auth domain (elevated, confirm required)."""
    return access.sync_domain(client, realm=realm, confirm=confirm)


@mcp.tool()
def proxmox_change_password(
    userid: str = "",
    password: str = "",
    confirm: bool = False,
) -> str:
    """Change user password (elevated, confirm required)."""
    return access.change_password(client, userid=userid, password=password, confirm=confirm)


@mcp.tool()
def proxmox_create_domain(
    realm: str = "",
    type: str = "",
    confirm: bool = False,
) -> str:
    """Create an auth domain (elevated, confirm required)."""
    return access.create_domain(client, realm=realm, type=type, confirm=confirm)


@mcp.tool()
def proxmox_update_domain(
    realm: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update an auth domain (elevated, confirm required)."""
    return access.update_domain(client, realm=realm, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_delete_domain(
    realm: str = "",
    confirm: bool = False,
) -> str:
    """Delete an auth domain (elevated, confirm required)."""
    return access.delete_domain(client, realm=realm, confirm=confirm)


@mcp.tool()
def proxmox_get_user_tfa_types(userid: str = "") -> str:
    """Get TFA types for a user via /access/users endpoint (read-only)."""
    return access.get_user_tfa_types(client, userid=userid)


@mcp.tool()
def proxmox_openid_auth_url(realm: str = "") -> str:
    """Get OpenID auth URL (read-only)."""
    return access.openid_auth_url(client, realm=realm)


@mcp.tool()
def proxmox_openid_login(
    realm: str = "",
    code: str = "",
    state: str = "",
) -> str:
    """Login via OpenID (read-only)."""
    return access.openid_login(client, realm=realm, code=code, state=state)


@mcp.tool()
def proxmox_update_snapshot_config(
    node: str | None = None,
    vmid: int | None = None,
    snapname: str = "",
    vmtype: str = "qemu",
    description: str | None = None,
    confirm: bool = False,
) -> str:
    """Update snapshot configuration (elevated, confirm required)."""
    return snapshots.update_snapshot_config(
        client, node=node, vmid=vmid, snapname=snapname,
        vmtype=vmtype, description=description, confirm=confirm,
    )


@mcp.tool()
def proxmox_delete_subscription(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Delete node subscription (elevated, confirm required)."""
    return nodes.delete_subscription(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_acquire_sdn_lock(confirm: bool = False) -> str:
    """Acquire SDN lock (elevated, confirm required)."""
    return sdn.acquire_sdn_lock(client, confirm=confirm)


@mcp.tool()
def proxmox_release_sdn_lock(confirm: bool = False) -> str:
    """Release SDN lock (elevated, confirm required)."""
    return sdn.release_sdn_lock(client, confirm=confirm)


@mcp.tool()
def proxmox_query_url_metadata(
    node: str | None = None,
    url: str = "",
) -> str:
    """Query URL metadata (file size/name/mime) on a node (read-only)."""
    return nodes.query_url_metadata(client, node=node, url=url)


@mcp.tool()
def proxmox_wake_on_lan(
    node: str | None = None,
    macaddr: str = "",
    confirm: bool = False,
) -> str:
    """Send Wake-on-LAN packet (elevated, confirm required)."""
    return nodes.wake_on_lan(client, node=node, macaddr=macaddr, confirm=confirm)


@mcp.tool()
def proxmox_get_storage_on_node(
    node: str | None = None,
    storage: str = "local",
) -> str:
    """Get detailed storage info on a node (read-only)."""
    return storage_mod.get_storage_on_node(client, node=node, storage=storage)


@mcp.tool()
def proxmox_copy_volume(
    node: str | None = None,
    storage: str = "local",
    volume: str = "",
    target: str = "",
    confirm: bool = False,
) -> str:
    """Copy a volume to another storage (elevated, confirm required)."""
    return storage_mod.copy_volume(
        client, node=node, storage=storage, volume=volume, target=target, confirm=confirm,
    )


@mcp.tool()
def proxmox_update_volume_attributes(
    node: str | None = None,
    storage: str = "local",
    volume: str = "",
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update volume attributes (elevated, confirm required)."""
    return storage_mod.update_volume_attributes(
        client, node=node, storage=storage, volume=volume, confirm=confirm, **kwargs,
    )


@mcp.tool()
def proxmox_file_restore_list(
    node: str | None = None,
    storage: str = "local",
) -> str:
    """List PBS backup file restore entries (read-only)."""
    return storage_mod.file_restore_list(client, node=node, storage=storage)


@mcp.tool()
def proxmox_file_restore_download(
    node: str | None = None,
    storage: str = "local",
    filepath: str = "",
) -> str:
    """Download a file from PBS backup (read-only)."""
    return storage_mod.file_restore_download(client, node=node, storage=storage, filepath=filepath)


@mcp.tool()
def proxmox_storage_import_metadata(
    node: str | None = None,
    storage: str = "local",
    volume: str = "",
) -> str:
    """Get storage import metadata for a volume (read-only)."""
    return storage_mod.storage_import_metadata(client, node=node, storage=storage, volume=volume)


@mcp.tool()
def proxmox_oci_registry_pull(
    node: str | None = None,
    storage: str = "local",
    image: str = "",
    confirm: bool = False,
) -> str:
    """Pull an OCI container image to storage (elevated, confirm required)."""
    return storage_mod.oci_registry_pull(client, node=node, storage=storage, image=image, confirm=confirm)


@mcp.tool()
def proxmox_cluster_config_apiversion() -> str:
    """Get cluster API version info (read-only)."""
    return cluster.cluster_config_apiversion(client)


@mcp.tool()
def proxmox_cluster_jobs_index() -> str:
    """List cluster jobs index (read-only)."""
    return cluster.cluster_jobs_index(client)


@mcp.tool()
def proxmox_list_realm_sync_jobs() -> str:
    """List realm synchronization jobs (read-only)."""
    return cluster.list_realm_sync_jobs(client)


@mcp.tool()
def proxmox_get_realm_sync_job(id: str = "") -> str:
    """Get a specific realm sync job (read-only)."""
    return cluster.get_realm_sync_job(client, id=id)


@mcp.tool()
def proxmox_vm_rrd(
    node: str | None = None,
    vmid: int | None = None,
    timeframe: str = "hour",
    cf: str = "AVERAGE",
    ds: str | None = None,
) -> str:
    """Get VM RRD data (read-only, may return PNG).

    timeframe: hour/day/week/month/year. cf: AVERAGE/MAX. ds: specific data source.
    """
    return lifecycle.vm_rrd(client, node=node, vmid=vmid, timeframe=timeframe, cf=cf, ds=ds)


@mcp.tool()
def proxmox_lxc_rrd(
    node: str | None = None,
    vmid: int | None = None,
    timeframe: str = "hour",
    cf: str = "AVERAGE",
    ds: str | None = None,
) -> str:
    """Get LXC container RRD data (read-only, may return PNG).

    timeframe: hour/day/week/month/year. cf: AVERAGE/MAX. ds: specific data source.
    """
    return lifecycle.lxc_rrd(client, node=node, vmid=vmid, timeframe=timeframe, cf=cf, ds=ds)


@mcp.tool()
def proxmox_lxc_rrddata(
    node: str | None = None,
    vmid: int | None = None,
    timeframe: str = "hour",
    cf: str = "AVERAGE",
) -> str:
    """Get LXC container RRD data points (read-only). timeframe: hour/day/week/month/year. cf: AVERAGE/MAX."""
    return lifecycle.lxc_rrddata(client, node=node, vmid=vmid, timeframe=timeframe, cf=cf)


@mcp.tool()
def proxmox_get_lxc_config(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get LXC container configuration (read-only)."""
    return lifecycle.get_lxc_config(client, node=node, vmid=vmid)


@mcp.tool()
def proxmox_get_lxc_status(
    node: str | None = None,
    vmid: int | None = None,
) -> str:
    """Get LXC container current status (read-only)."""
    return lifecycle.get_lxc_status(client, node=node, vmid=vmid)


@mcp.tool()
def proxmox_remote_migrate_lxc(
    node: str | None = None,
    vmid: int | None = None,
    target: str | None = None,
    target_endpoint: str | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Remote migrate an LXC container to another cluster (elevated). Requires confirm=true."""
    return lifecycle.remote_migrate_lxc(
        client, node=node, vmid=vmid, target=target,
        target_endpoint=target_endpoint, confirm=confirm, **kwargs,
    )


@mcp.tool()
def proxmox_move_lxc_volume(
    node: str | None = None,
    vmid: int | None = None,
    volume: str = "rootfs",
    storage: str | None = None,
    target_vmid: int | None = None,
    target_volume: str | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Move an LXC container volume to different storage or container (elevated). Requires confirm=true."""
    return lifecycle.move_lxc_volume(
        client, node=node, vmid=vmid, volume=volume,
        storage=storage, target_vmid=target_vmid,
        target_volume=target_volume, confirm=confirm, **kwargs,
    )


@mcp.tool()
def proxmox_get_vm_config(
    node: str | None = None,
    vmid: int | None = None,
    current: bool = False,
) -> str:
    """Get VM configuration (read-only). Set current=True for current config instead of pending."""
    return lifecycle.get_vm_config(client, node=node, vmid=vmid, current=current)


@mcp.tool()
def proxmox_update_vm_config(
    node: str | None = None,
    vmid: int | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update VM configuration (elevated, confirm required, asynchronous API)."""
    return lifecycle.update_vm_config(client, node=node, vmid=vmid, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_vm_rrddata(
    node: str | None = None,
    vmid: int | None = None,
    timeframe: str = "hour",
    cf: str = "AVERAGE",
) -> str:
    """Get VM RRD data points (read-only). timeframe: hour/day/week/month/year. cf: AVERAGE/MAX."""
    return lifecycle.vm_rrddata(client, node=node, vmid=vmid, timeframe=timeframe, cf=cf)


@mcp.tool()
def proxmox_remote_migrate_vm(
    node: str | None = None,
    vmid: int | None = None,
    target_address: str | None = None,
    target_node: str | None = None,
    target_storage: str | None = None,
    confirm: bool = False,
) -> str:
    """Remote migrate a VM to another cluster (elevated, confirm required, EXPERIMENTAL)."""
    return lifecycle.remote_migrate_vm(
        client, node=node, vmid=vmid, target_address=target_address,
        target_node=target_node, target_storage=target_storage, confirm=confirm,
    )


@mcp.tool()
def proxmox_list_ha_rules() -> str:
    """List HA rules in the cluster (read-only)."""
    return ha.list_ha_rules(client)


@mcp.tool()
def proxmox_create_ha_rule(
    group: str = "",
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    """Create an HA rule (elevated, confirm required)."""
    return ha.create_ha_rule(client, group=group, comment=comment, confirm=confirm)


@mcp.tool()
def proxmox_get_ha_rule(rule: str = "") -> str:
    """Get HA rule configuration (read-only)."""
    return ha.get_ha_rule(client, rule=rule)


@mcp.tool()
def proxmox_update_ha_rule(
    rule: str = "",
    comment: str | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update an HA rule (elevated, confirm required)."""
    return ha.update_ha_rule(client, rule=rule, comment=comment, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_delete_ha_rule(
    rule: str = "",
    confirm: bool = False,
) -> str:
    """Delete an HA rule (elevated, confirm required)."""
    return ha.delete_ha_rule(client, rule=rule, confirm=confirm)


@mcp.tool()
def proxmox_get_ha_group(group: str = "") -> str:
    """Get HA group configuration (read-only)."""
    return ha.get_ha_group(client, group=group)


@mcp.tool()
def proxmox_update_ha_group(
    group: str = "",
    comment: str | None = None,
    nodes: str | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Update an HA group (elevated, confirm required)."""
    return ha.update_ha_group(client, group=group, comment=comment, nodes=nodes, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_delete_ha_group(
    group: str = "",
    confirm: bool = False,
) -> str:
    """Delete an HA group (elevated, confirm required)."""
    return ha.delete_ha_group(client, group=group, confirm=confirm)


@mcp.tool()
def proxmox_arm_ha(confirm: bool = False) -> str:
    """Arm the HA manager (elevated, confirm required)."""
    return ha.arm_ha(client, confirm=confirm)


@mcp.tool()
def proxmox_disarm_ha(confirm: bool = False) -> str:
    """Disarm the HA manager (elevated, confirm required)."""
    return ha.disarm_ha(client, confirm=confirm)


@mcp.tool()
def proxmox_ha_manager_status() -> str:
    """Get HA manager status (read-only)."""
    return ha.ha_manager_status(client)


@mcp.tool()
def proxmox_create_ticket(
    username: str = "",
    password: str = "",
) -> str:
    """Create an authentication ticket (read-only, returns ticket+CSRF token)."""
    return access.create_ticket(client, username=username, password=password)


@mcp.tool()
def proxmox_create_vnc_ticket(
    port: int | None = None,
    vnc: str | None = None,
) -> str:
    """Create a VNC ticket (read-only, VNC auth)."""
    return access.create_vnc_ticket(client, port=port, vnc=vnc)


@mcp.tool()
def proxmox_lxc_sendkey(
    node: str | None = None,
    vmid: int | None = None,
    key: str = "",
    confirm: bool = False,
) -> str:
    """Send a key press to an LXC container (elevated, confirm required)."""
    return lifecycle.lxc_sendkey(client, node=node, vmid=vmid, key=key, confirm=confirm)


@mcp.tool()
def proxmox_check_subscription(
    node: str | None = None,
    confirm: bool = False,
) -> str:
    """Check for subscription updates from Proxmox servers (elevated, confirm required)."""
    return nodes.check_subscription(client, node=node, confirm=confirm)


@mcp.tool()
def proxmox_get_directory_detail(
    node: str | None = None,
    name: str = "",
) -> str:
    """Get directory storage details (read-only)."""
    return disks.get_directory_detail(client, node=node, name=name)


@mcp.tool()
def proxmox_get_lvmthin_detail(
    node: str | None = None,
    name: str = "",
) -> str:
    """Get LVM thin pool details (read-only)."""
    return disks.get_lvmthin_detail(client, node=node, name=name)


@mcp.tool()
def proxmox_reload_service(
    node: str | None = None,
    service: str = "",
    confirm: bool = False,
) -> str:
    """Reload a service on a node (elevated, confirm required)."""
    return nodes.reload_service(client, node=node, service=service, confirm=confirm)


@mcp.tool()
def proxmox_get_next_vmid() -> str:
    """Get the next available VMID (read-only)."""
    return discovery.get_next_vmid(client)


@mcp.tool()
def proxmox_generate_cluster_config(
    node: str | None = None,
    confirm: bool = False,
    **kwargs: str,
) -> str:
    """Generate cluster config for joining (elevated, confirm required, DANGEROUS)."""
    return cluster.generate_cluster_config(client, node=node, confirm=confirm, **kwargs)


@mcp.tool()
def proxmox_remove_cluster_node(
    node: str = "",
    confirm: bool = False,
) -> str:
    """Remove a node from the cluster (elevated, confirm required, DANGEROUS)."""
    return cluster.remove_cluster_node(client, node=node, confirm=confirm)


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
