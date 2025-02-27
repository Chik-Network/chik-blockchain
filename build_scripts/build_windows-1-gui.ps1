# $env:path should contain a path to editbin.exe and signtool.exe

$ErrorActionPreference = "Stop"

git status

Set-Location -Path "..\" -PassThru
git submodule update --init chik-blockchain-gui

Set-Location -Path ".\chik-blockchain-gui" -PassThru

Write-Output "   ---"
Write-Output "Build GUI npm modules"
Write-Output "   ---"
$Env:NODE_OPTIONS = "--max-old-space-size=3000"

Write-Output "npx lerna clean -y"
npx lerna clean -y # Removes packages/*/node_modules
Write-Output "npm ci"
npm ci
# Audit fix does not currently work with Lerna. See https://github.com/lerna/lerna/issues/1663
# npm audit fix

git status

Write-Output "npm run build"
npm run build
If ($LastExitCode -gt 0){
    Throw "npm run build failed!"
}

# Remove unused packages
Remove-Item node_modules -Recurse -Force

# Other than `chik-blockchain-gui/package/gui`, all other packages are no longer necessary after build.
# Since these unused packages make cache unnecessarily fat, unused packages should be removed.
Write-Output "Remove unused @chik-network packages to make cache slim"
Remove-Item packages\api -Recurse -Force
Remove-Item packages\api-react -Recurse -Force
Remove-Item packages\core -Recurse -Force
Remove-Item packages\icons -Recurse -Force
Remove-Item packages\wallets -Recurse -Force

# Remove unused fat npm modules from the gui package
#Set-Location -Path ".\packages\gui\node_modules" -PassThru
#Write-Output "Remove unused node_modules in the gui package to make cache slim more"
#Remove-Item electron\dist -Recurse -Force # ~186MB
#Remove-Item "@mui" -Recurse -Force # ~71MB
#Remove-Item typescript -Recurse -Force # ~63MB

# Remove `packages/gui/node_modules/@chik-network` because it causes an error on later `electron-packager` command
#Remove-Item "@chik-network" -Recurse -Force
