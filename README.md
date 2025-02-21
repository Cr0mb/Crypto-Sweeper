![image](https://github.com/user-attachments/assets/887bad3b-dd46-43b7-b8c4-4b41aaa9fa14)


# Crypto-Sweeper
Crypto Sweeper is a Python-based cryptocurrency wallet generator and balance checker. It generates Bitcoin and Ethereum wallets using BIP-39 mnemonics and checks their balances via online APIs. If a wallet contains funds, it is saved to a file.


## Features

- Generate Bitcoin and Ethereum wallets from 12 or 24-word mnemonics
- Derive multiple Bitcoin address formats (Legacy, Nested SegWit, Native SegWit)
- Convert Ethereum addresses to checksum format
- Check wallet balances using public APIs
- Automatically save wallets with non-zero balances
- User-friendly terminal interface with color-coded output

## Requirements

- Python 3.x
```
pip install requests colorama bip_utils web3 eth_utils
```

## Disclaimer
> This script is for educational and research purposes only. The author is not responsible for any misuse or unethical activities performed using this tool.
