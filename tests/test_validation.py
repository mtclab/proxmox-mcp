import pytest

from proxmox_mcp.utils import (
    validate_disk_size,
    validate_iface_name,
    validate_node_name,
    validate_storage_name,
    validate_vmid,
)


class TestValidateNodeName:
    def test_valid_simple(self):
        validate_node_name("pve")

    def test_valid_with_dots(self):
        validate_node_name("node1.example.com")

    def test_valid_with_hyphens(self):
        validate_node_name("my-node-1")

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="Invalid node name"):
            validate_node_name("")

    def test_rejects_spaces(self):
        with pytest.raises(ValueError, match="Invalid node name"):
            validate_node_name("my node")

    def test_rejects_special_chars(self):
        with pytest.raises(ValueError, match="Invalid node name"):
            validate_node_name("node!@#")

    def test_rejects_starts_with_dot(self):
        with pytest.raises(ValueError, match="Invalid node name"):
            validate_node_name(".hidden")


class TestValidateVmid:
    def test_valid_positive_int(self):
        validate_vmid(100)

    def test_none_passes(self):
        validate_vmid(None)

    def test_rejects_zero(self):
        with pytest.raises(ValueError, match="Invalid vmid"):
            validate_vmid(0)

    def test_rejects_negative(self):
        with pytest.raises(ValueError, match="Invalid vmid"):
            validate_vmid(-1)

    def test_rejects_string(self):
        with pytest.raises(ValueError, match="Invalid vmid"):
            validate_vmid("100")


class TestValidateStorageName:
    def test_valid_simple(self):
        validate_storage_name("local")

    def test_valid_with_dots(self):
        validate_storage_name("local-lvm")

    def test_valid_with_underscores(self):
        validate_storage_name("my_storage")

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="Invalid storage name"):
            validate_storage_name("")

    def test_rejects_spaces(self):
        with pytest.raises(ValueError, match="Invalid storage name"):
            validate_storage_name("my storage")


class TestValidateIfaceName:
    def test_valid_bridge(self):
        validate_iface_name("vmbr0")

    def test_valid_eth(self):
        validate_iface_name("eno1")

    def test_valid_with_colon(self):
        validate_iface_name("eth0:1")

    def test_valid_with_dot(self):
        validate_iface_name("eth0.100")

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="Invalid interface name"):
            validate_iface_name("")

    def test_rejects_spaces(self):
        with pytest.raises(ValueError, match="Invalid interface name"):
            validate_iface_name("bad iface")


class TestValidateDiskSize:
    def test_integer_passthrough(self):
        assert validate_disk_size(32) == "32"

    def test_string_integer(self):
        assert validate_disk_size("32") == "32"

    def test_string_with_G(self):
        assert validate_disk_size("32G") == "32"

    def test_string_with_GiB(self):
        assert validate_disk_size("10GiB") == "10"

    def test_string_with_T(self):
        assert validate_disk_size("1T") == "1024"

    def test_string_with_TiB(self):
        assert validate_disk_size("2TiB") == "2048"

    def test_invalid_string_raises(self):
        with pytest.raises(ValueError, match="Invalid disk_size"):
            validate_disk_size("abc")

    def test_invalid_unit_raises(self):
        with pytest.raises(ValueError, match="Invalid disk_size"):
            validate_disk_size("10MB")

    def test_float_numeric_part_raises(self):
        with pytest.raises(ValueError, match="Invalid disk_size"):
            validate_disk_size("1.5G")

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="Invalid disk_size"):
            validate_disk_size([10])
