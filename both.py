import random
import time
import requests
from colorama import Fore, Style, init
import os
import subprocess
import tarfile
import sys
from bip_utils import (
    Bip39MnemonicGenerator, Bip39SeedGenerator, Bip84, Bip84Coins,
    Bip49, Bip49Coins, Bip44, Bip44Coins, Bip44Changes
)
from eth_utils import to_checksum_address
from web3 import Web3

init(autoreset=True)

BLOCKCYPHER_API_URL = "https://api.blockcypher.com/v1/eth/main/addrs/{}"
BTC_API_URL = "https://blockstream.info/api/address/{}"

def generate_mnemonic(num_words=12):
    if num_words not in [12, 24]:
        raise ValueError(f"{Fore.RED}Error: Choose 12 or 24 words only{Style.RESET_ALL}")
    return Bip39MnemonicGenerator().FromWordsNumber(num_words)

def derive_addresses(mnemonic):
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    
    bip44_btc = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    btc_legacy_address = bip44_btc.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()

    bip49_btc = Bip49.FromSeed(seed_bytes, Bip49Coins.BITCOIN)
    btc_nested_segwit_address = bip49_btc.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()

    bip84_btc = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
    btc_native_segwit_address = bip84_btc.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
    
    bip44_eth = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    eth_address = bip44_eth.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
    
    return btc_legacy_address, btc_nested_segwit_address, btc_native_segwit_address, to_checksum_address(eth_address), mnemonic.ToStr()

def check_btc_balance(address):
    try:
        response = requests.get(BTC_API_URL.format(address), timeout=10)
        data = response.json()
        balance_satoshis = data.get("chain_stats", {}).get("funded_txo_sum", 0) - data.get("chain_stats", {}).get("spent_txo_sum", 0)
        return balance_satoshis / 1e8, balance_satoshis
    except Exception:
        return None, None

def check_eth_balance(address):
    try:
        response = requests.get(BLOCKCYPHER_API_URL.format(address), timeout=10)
        data = response.json()
        balance_wei = data.get("balance", 0)
        return balance_wei / 1e18, balance_wei
    except Exception:
        return None, None

def save_wallet(mnemonic, address, balance, currency):
    with open("wallets.txt", "a") as f:
        f.write(f"Mnemonic: {mnemonic}\nAddress: {address}\nBalance: {balance:.8f} {currency}\n\n")

def generate_wallets(option):
    try:
        while True:
            num_words = 12 if option == "12" else 24 if option == "24" else random.choice([12, 24])
            btc_legacy, btc_nested, btc_native, eth_address, mnemonic = derive_addresses(generate_mnemonic(num_words))
            
            print(f"\n{Fore.CYAN}{'=' * 40}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Generated {num_words}-word Wallet:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Mnemonic: {Style.BRIGHT}{mnemonic}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}BTC Legacy: {Fore.WHITE}{btc_legacy}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}BTC Nested: {Fore.WHITE}{btc_nested}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}BTC Native: {Fore.WHITE}{btc_native}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}ETH Address: {Fore.WHITE}{eth_address}{Style.RESET_ALL}")
            
            for address, currency, checker in [(btc_legacy, "BTC", check_btc_balance), 
                                               (btc_nested, "BTC", check_btc_balance), 
                                               (btc_native, "BTC", check_btc_balance), 
                                               (eth_address, "ETH", check_eth_balance)]:
                print(f"{Fore.BLUE}Checking balance for {address}...{Style.RESET_ALL}")
                balance, _ = checker(address)
                
                if balance is not None:
                    balance_msg = f"{Fore.GREEN}{balance:.8f} {currency}{Style.RESET_ALL}"
                    if balance > 0:
                        save_wallet(mnemonic, address, balance, currency)
                        print(f"{Fore.LIGHTGREEN_EX}[SAVED] {address} - {balance_msg}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}{address}: {balance_msg}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}{address}: Balance check failed{Style.RESET_ALL}")
            
            print(f"{Fore.CYAN}{'=' * 40}{Style.RESET_ALL}\n")
            time.sleep(2)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Process stopped by user. Exiting...{Style.RESET_ALL}")

if __name__ == "__main__":
    print(f"{Fore.GREEN}{' ' * 10}Crypto Sweeper{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{' ' * 10}Made by Cr0mb{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}{'=' * 30}{Style.RESET_ALL}\n")
    
    print(f"{Fore.MAGENTA}Choose an option:{Style.RESET_ALL}")
    print(f"{Fore.BLUE}1. Generate 12-word wallets{Style.RESET_ALL}")
    print(f"{Fore.BLUE}2. Generate 24-word wallets{Style.RESET_ALL}")
    print(f"{Fore.BLUE}3. Generate both randomly{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}{'=' * 30}{Style.RESET_ALL}\n")
    
    choice = input(f"{Fore.YELLOW}Enter your choice (12/24/both): {Style.RESET_ALL}").strip().lower()
    generate_wallets(choice)
