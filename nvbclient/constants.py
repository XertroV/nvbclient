ENDIAN = 'big'
MSG_PREFIX = b'NVB'
USE_COMPRESSED = False
PRIMARY = 'primary'
NET_CODE = {
    'bitcoin': 'BTC',
    'testnet': 'XTN',
}
ELECTRUM_SERVERS = {
    #'ecdsa.org': 50001,
    'ecdsa.net': 50001,  # good
    #'electrum.hachre.de': 50001,
    #'electrum.novit.ro': 50001,
    #'electrum.coinwallet.me': 50001,
    #'cube.l0g.in': 50001,
    'bitcoin.epicinet.net': 50001,  # good
    'h.1209k.com': 50001,  # good but gives hash return for tx already in blockchain
    #'electrum.electricnewyear.net': 50001,
    'erbium.sytes.net': 50001,  # good
    #'e2.pdmc.net': 50001,
    'electrum.no-ip.org': 50001,  # good
    'electrum.thwg.org': 50001,  # good
    #'electrum.stepkrav.pw': 50001,
}
DUST = 5460
MIN_FEE = 1000