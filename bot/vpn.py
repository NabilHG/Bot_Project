import asyncio
import aiohttp
import subprocess

class VPNManager:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def get_public_ip(self):
        async with self.session.get("https://api.ipify.org") as response:
            return await response.text()

    async def activate_vpn(self, config_path):
        print(config_path)
        original_ip = await self.get_public_ip()
        print(original_ip, "IP1")

        try:
            cmd = f"sudo openvpn --config {config_path} --log /var/log/openvpn.log"
            process = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            while True:
                if await self.is_vpn_active():
                    print(f"VPN activated, exiting while loop: {config_path}")
                    break
                else:
                    await asyncio.sleep(1)

            await asyncio.sleep(5)

            vpn_ip = await self.get_public_ip()
            print(vpn_ip, "IP2")

            if original_ip == vpn_ip:
                print("VPN IP and original IP are the same. Something went wrong.")
            else:
                print("VPN activated successfully and IP has changed.")

        except subprocess.CalledProcessError as ex:
            print(f"Error while activating VPN: {ex}")

    async def deactivate_vpn(self):
        try:
            cmd = "sudo pkill openvpn"

            process = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            while True:
                if not await self.is_vpn_active():
                    break
                else:
                    await asyncio.sleep(1)
            print("VPN deactivated")

        except subprocess.CalledProcessError as ex:
            print(f"Error while deactivating VPN: {ex}")

    async def is_vpn_active(self):
        try:
            result = await asyncio.create_subprocess_shell(
                "ip link", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()

            stdout_decoded = stdout.decode()
            stderr_decoded = stderr.decode()

            print(f"stderr: {stderr_decoded}")
            # print(f"stdout: {stdout_decoded}")

            if any("tun" in line and "UP" in line for line in stdout_decoded.splitlines()):
                print("VPN is active")
                return True
            else:
                print("VPN is not active")
                return False

        except asyncio.CancelledError:
            raise
        except Exception as ex:
            print(f"Error while checking VPN state: {ex}")
            return False

    async def contains_info(self, responses, substring):
        if isinstance(responses, dict):
            for key, value in responses.items():
                if await self.contains_info(value, substring):
                    return True
        elif isinstance(responses, list):
            for item in responses:
                if await self.contains_info(item, substring):
                    return True
        elif isinstance(responses, str):
            if substring in responses:
                return True
        return False

    async def close(self):
        await self.session.close()
