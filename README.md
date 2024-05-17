# Chik-Blockchain

**Chik** is a modern community-centric green cryptocurrency based on a proof-of-space-and-time consensus algorithm. 

All premined coins(21000000XCK) haved been send to burn address(2024-05-10):
xck1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqm6ksjy75z0

For more information, see our website and downloads at <a href="https://www.chiknetwork.com">Chik Network</a>.
<p>You can learn more in the Chik Wiki: <a href="https://github.com/Chik-Network/chik-blockchain/wiki/Chik-Blockchain-Wiki">Quick Start Guide</a></p>
<p>Discord Channel: (https://discord.gg/SNbcMMvNBE).</p>

<p>Full Node List Here:<a href="https://alltheblocks.net/chik/peers" rel="nofollow"> Full Node IP's</a></p>
<p>Port: 9678</p>

<h1>Windows Installer</h1>
<p>Download the Windows installer (exe) or Zip file - <a href="https://github.com/Chik-Network/chik-blockchain/releases" rel="nofollow">Chik Blockchain Windows</a></p>
<p>As the Chik code signing certificate is new you will likely have to ask to keep the download and when you run the installer, you will have to choose "More Info" and "Run Anyway" to be able to run the installer. There is no need to use the command line. Some Windows antivirus applications are seeing the download as a false positive. You can see the entire source code and build method here, so we think it's safe for you to ask those tools to ignore it. Running the installer while plotting on a previous version will stop your plotting process, so be careful.</p>

<h1>Ubuntu/Debian Install</h1>
<p>sudo apt-get update</p>
<p>sudo apt-get upgrade -y</p>
<p># Install Git</p>
<p>sudo apt install git -y</p>
<p># Checkout the source and install</p>
<p>git clone https://github.com/Chik-Network/chik-blockchain.git --recurse-submodules</p>
<p>cd chik-blockchain</p>
<p>sh install.sh</p>
<p>. ./activate</p>
<p>chik init</p>
<p>#add your plot directories</p>
<p>chik plots add -d /yourplotpath</p>
<p>chik start farmer</p>
<p># The GUI requires you have Ubuntu Desktop or a similar windowing system installed.<p>
<p># You can not install and run the GUI as root</p>
<p>cd /home/'yourusername'/chik-blockchain/</p>
<p>. ./activate</p>
<p>sh install-gui.sh</p>
<p>cd chik-blockchain-gui</p>
<p>npm run electron &</p>

<h1>Ubuntu/Debian Update</h1>
<p># Stop all chik processes</p>
<p># Delete your 'chik-blockchain' folder, not your '.chik' folder</p>
<p># Clone 'chik-blockchain'</p>
<p>chik stop -d all</p>
<p>rm -rf /home/'yourusername'/chik-blockchain</p>
<p>git clone https://github.com/Chik-Network/chik-blockchain.git --recurse-submodules</p>
<p>cd chik-blockchain</p>
<p>sh install.sh</p>
<p>. ./activate</p>
<p>chik init</p>
<p>chik start farmer</p>
<p>*Note, If you receive errors during the installation process, your system is missing dependencies. In this case, thank you for trying :)</p>
