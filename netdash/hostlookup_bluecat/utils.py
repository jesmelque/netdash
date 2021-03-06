from typing import Iterable, Optional
from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address, ip_address

from django.core.exceptions import ValidationError

from netaddr import EUI

from hostlookup_bluecat.bluecat import lookup_cidr, get_connection, BlueCatAddress


@dataclass
class BlueCatHostLookupResult:
    mac: EUI
    ipv4: Optional[IPv4Address]
    ipv6: Optional[IPv6Address]
    hostnames: Iterable[str]


def transform(bca: BlueCatAddress) -> BlueCatHostLookupResult:
    return BlueCatHostLookupResult(
        bca.mac,
        bca.address,
        None,
        bca.hostnames,
    )


def host_lookup(q: str, bluecat_config: int) -> Iterable[BlueCatHostLookupResult]:
    if bluecat_config is None:
        raise ValidationError('bluecat_config is required.')
    try:
        ip = ip_address(q)
    except ValueError as ve:
        raise ValidationError(ve)
    with get_connection() as bc:
        bc_network = lookup_cidr(bc, ip, bluecat_config)
    return [transform(bca) for bca in bc_network.bc_addresses]
