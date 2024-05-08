from __future__ import annotations

from typing import Any, Dict

import pytest

from chik.wallet.util.address_type import AddressType, ensure_valid_address, is_valid_address


@pytest.mark.parametrize("prefix", [None])
def test_xck_hrp_for_default_config(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    assert AddressType.XCK.hrp(config) == "xck"


@pytest.mark.parametrize("prefix", ["txck"])
def test_txck_hrp_for_testnet(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    assert AddressType.XCK.hrp(config) == "txck"


@pytest.mark.parametrize("prefix", [None])
def test_is_valid_address_xck(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    valid = is_valid_address(
        "xck1mnr0ygu7lvmk3nfgzmncfk39fwu0dv933yrcv97nd6pmrt7fzmhs0kyx8x", allowed_types={AddressType.XCK}, config=config
    )
    assert valid is True


@pytest.mark.parametrize("prefix", ["txck"])
def test_is_valid_address_txck(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    # TXCK address validation requires a config
    valid = is_valid_address(
        "txck1mnr0ygu7lvmk3nfgzmncfk39fwu0dv933yrcv97nd6pmrt7fzmhsz3rsx4",
        allowed_types={AddressType.XCK},
        config=config,
    )
    assert valid is True


@pytest.mark.parametrize("prefix", [None])
def test_is_valid_address_xck_bad_address(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    valid = is_valid_address(
        "xck1mnr0ygu7lvmk3nfgzmncfk39fwu0dv933yrcv97nd6pmrt7fzmhs0xxxxx", allowed_types={AddressType.XCK}, config=config
    )
    assert valid is False


@pytest.mark.parametrize("prefix", [None])
def test_is_valid_address_nft(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    valid = is_valid_address(
        "nft1mx2nkvml2eekjtqwdmxvmf3js8g083hpszzhkhtwvhcss8efqzhqtza773", allowed_types={AddressType.NFT}, config=config
    )
    assert valid is True


@pytest.mark.parametrize("prefix", ["txck"])
def test_is_valid_address_nft_with_testnet(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    valid = is_valid_address(
        "nft1mx2nkvml2eekjtqwdmxvmf3js8g083hpszzhkhtwvhcss8efqzhqtza773", allowed_types={AddressType.NFT}, config=config
    )
    assert valid is True


@pytest.mark.parametrize("prefix", [None])
def test_is_valid_address_nft_bad_address(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    valid = is_valid_address(
        "nft1mx2nkvml2eekjtqwdmxvmf3js8g083hpszzhkhtwvhcss8efqzhqtxxxxx", allowed_types={AddressType.NFT}, config=config
    )
    assert valid is False


@pytest.mark.parametrize("prefix", [None])
def test_is_valid_address_did(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    valid = is_valid_address(
        "did:chik:14jxdtqcyp3gk8ka0678eq8mmtnktgpmp2vuqq3vtsl2e5qr7fyrsr9gsr7",
        allowed_types={AddressType.DID},
        config=config,
    )
    assert valid is True


@pytest.mark.parametrize("prefix", ["txck"])
def test_is_valid_address_did_with_testnet(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    valid = is_valid_address(
        "did:chik:14jxdtqcyp3gk8ka0678eq8mmtnktgpmp2vuqq3vtsl2e5qr7fyrsr9gsr7",
        allowed_types={AddressType.DID},
        config=config,
    )
    assert valid is True


@pytest.mark.parametrize("prefix", [None])
def test_is_valid_address_did_bad_address(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    valid = is_valid_address(
        "did:chik:14jxdtqcyp3gk8ka0678eq8mmtnktgpmp2vuqq3vtsl2e5qr7fyrsrxxxxx",
        allowed_types={AddressType.DID},
        config=config,
    )
    assert valid is False


@pytest.mark.parametrize("prefix", [None])
def test_ensure_valid_address_xck(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    address = ensure_valid_address(
        "xck1mnr0ygu7lvmk3nfgzmncfk39fwu0dv933yrcv97nd6pmrt7fzmhs0kyx8x", allowed_types={AddressType.XCK}, config=config
    )
    assert address == "xck1mnr0ygu7lvmk3nfgzmncfk39fwu0dv933yrcv97nd6pmrt7fzmhs0kyx8x"


@pytest.mark.parametrize("prefix", ["txck"])
def test_ensure_valid_address_txck(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    address = ensure_valid_address(
        "txck1mnr0ygu7lvmk3nfgzmncfk39fwu0dv933yrcv97nd6pmrt7fzmhsz3rsx4",
        allowed_types={AddressType.XCK},
        config=config,
    )
    assert address == "txck1mnr0ygu7lvmk3nfgzmncfk39fwu0dv933yrcv97nd6pmrt7fzmhsz3rsx4"


@pytest.mark.parametrize("prefix", [None])
def test_ensure_valid_address_xck_bad_address(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    with pytest.raises(ValueError):
        ensure_valid_address(
            "xck1mnr0ygu7lvmk3nfgzmncfk39fwu0dv933yrcv97nd6pmrt7fzmhs0xxxxx",
            allowed_types={AddressType.XCK},
            config=config,
        )


@pytest.mark.parametrize("prefix", [None])
def test_ensure_valid_address_nft(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    address = ensure_valid_address(
        "nft1mx2nkvml2eekjtqwdmxvmf3js8g083hpszzhkhtwvhcss8efqzhqtza773", allowed_types={AddressType.NFT}, config=config
    )
    assert address == "nft1mx2nkvml2eekjtqwdmxvmf3js8g083hpszzhkhtwvhcss8efqzhqtza773"


@pytest.mark.parametrize("prefix", [None])
def test_ensure_valid_address_nft_bad_address(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    with pytest.raises(ValueError):
        ensure_valid_address(
            "nft1mx2nkvml2eekjtqwdmxvmf3js8g083hpszzhkhtwvhcss8efqzhqtxxxxx",
            allowed_types={AddressType.NFT},
            config=config,
        )


@pytest.mark.parametrize("prefix", [None])
def test_ensure_valid_address_did(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    address = ensure_valid_address(
        "did:chik:14jxdtqcyp3gk8ka0678eq8mmtnktgpmp2vuqq3vtsl2e5qr7fyrsr9gsr7",
        allowed_types={AddressType.DID},
        config=config,
    )
    assert address == "did:chik:14jxdtqcyp3gk8ka0678eq8mmtnktgpmp2vuqq3vtsl2e5qr7fyrsr9gsr7"


@pytest.mark.parametrize("prefix", [None])
def test_ensure_valid_address_did_bad_address(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    with pytest.raises(ValueError):
        ensure_valid_address(
            "did:chik:14jxdtqcyp3gk8ka0678eq8mmtnktgpmp2vuqq3vtsl2e5qr7fyrsrxxxxx",
            allowed_types={AddressType.DID},
            config=config,
        )


@pytest.mark.parametrize("prefix", [None])
def test_ensure_valid_address_bad_length(config_with_address_prefix: Dict[str, Any]) -> None:
    config = config_with_address_prefix
    with pytest.raises(ValueError):
        ensure_valid_address("xck1qqqqqqqqqqqqqqqq4w6405", allowed_types={AddressType.XCK}, config=config)
