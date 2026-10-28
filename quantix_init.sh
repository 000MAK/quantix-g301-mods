#!/data/data/com.termux/files/usr/bin/bash
# Termux first-run setup. In Termux:  termux-setup-storage   then   bash ~/storage/downloads/quantix_init.sh
set -e
pkg update -y && pkg install -y python git openssh
pip install --upgrade pip
pip install numpy pandas
O='\e[38;5;208m'; T='\e[38;5;44m'; G='\e[38;5;245m'; W='\e[38;5;255m'; R='\e[0m'
printf '%b\n' \
  "${O}     /\\_/\\    ${T}  S I M B A   K O M U T A   M E R K E Z İ" \
  "${O}    ( ${T}o${O}.${T}o${O} )   ${G}  python · git · ssh · pandas" \
  "${O}     > ^ <  ${T}==========${W})${T}━━━━━━━━━━━━━━━━${R}" > ~/.simba_banner
grep -q simba_banner ~/.bashrc 2>/dev/null || echo 'cat ~/.simba_banner' >> ~/.bashrc
grep -q 'PS1=' ~/.bashrc 2>/dev/null || echo 'PS1="\[\e[38;5;44m\]\w \[\e[38;5;208m\]❯\[\e[0m\] "' >> ~/.bashrc
echo "Kurulum bitti. Termux'u kapatıp açınca Simba seni karşılar."
