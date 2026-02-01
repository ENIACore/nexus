<a id="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<br />
<div align="center">
  <h3 align="center">Nexus Server</h3>

  <p align="center">
    Automated self-hosted server setup with security hardening and reverse proxy configuration
    <br />
    <a href="https://github.com/ENIACore/nexus"><strong>Explore the docs</strong></a>
    <br />
    <br />
    <a href="https://github.com/ENIACore/nexus/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/ENIACore/nexus/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#what-gets-installed">What Gets Installed</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## About The Project

Nexus is an automated installation script that transforms a fresh Ubuntu server into a fully-configured self-hosted platform. It deploys popular services like Nextcloud, Vaultwarden, and Jellyfin with production-ready security hardening, reverse proxy configuration, and automated SSL certificate management through Cloudflare.

The project emphasizes security and ease of use, handling everything from firewall configuration to fail2ban setup, allowing you to have a production-ready server in minutes rather than hours.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Python][Python-badge]][Python-url]
* [![Bash][Bash-badge]][Bash-url]
* [![Docker][Docker-badge]][Docker-url]
* [![Nginx][Nginx-badge]][Nginx-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Prerequisites

Before running the installation script, ensure you have:

* Ubuntu Server LTS
* Root or sudo access
* Active internet connection
* (Optional) Cloudflare account for DNS and SSL management

### Installation

Run this command in your Ubuntu terminal to start the installation:

```bash
curl -fsSL https://raw.githubusercontent.com/ENIACore/nexus/main/install.py -o /tmp/nexus-install.py && sudo python3 /tmp/nexus-install.py; rm -f /tmp/nexus-install.py
```

The script will guide you through the setup process and configure all services automatically.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## What Gets Installed

The Nexus installation includes the following services and security features:

**Services:**
- **Nextcloud** - Self-hosted file sync and share platform
- **Vaultwarden** - Lightweight Bitwarden server implementation
- **Jellyfin** - Media server for your personal media collection
- **qBittorrent** - Torrent client with Web UI
- **Gluetun VPN** - VPN client container for secure networking

**Security & Infrastructure:**
- **Nginx** - Reverse proxy with SSL termination
- **Cloudflare DNS & SSL** - Automated certificate management
- **Fail2ban** - Intrusion prevention system
- **UFW Firewall** - Uncomplicated firewall configuration

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap

- [ ] Add support for additional Linux distributions
- [ ] Implement automated backup solutions
- [ ] Add monitoring and alerting system
- [ ] Create web-based configuration interface
- [ ] Add support for additional self-hosted services

See the [open issues](https://github.com/ENIACore/nexus/issues) for a full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/ENIACore/nexus/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=ENIACore/nexus" alt="contrib.rocks image" />
</a>

## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

Project Link: [https://github.com/ENIACore/nexus](https://github.com/ENIACore/nexus)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/ENIACore/nexus.svg?style=for-the-badge
[contributors-url]: https://github.com/ENIACore/nexus/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/ENIACore/nexus.svg?style=for-the-badge
[forks-url]: https://github.com/ENIACore/nexus/network/members
[stars-shield]: https://img.shields.io/github/stars/ENIACore/nexus.svg?style=for-the-badge
[stars-url]: https://github.com/ENIACore/nexus/stargazers
[issues-shield]: https://img.shields.io/github/issues/ENIACore/nexus.svg?style=for-the-badge
[issues-url]: https://github.com/ENIACore/nexus/issues
[license-shield]: https://img.shields.io/github/license/ENIACore/nexus.svg?style=for-the-badge
[license-url]: https://github.com/ENIACore/nexus/blob/main/LICENSE
[Python-badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Bash-badge]: https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white
[Bash-url]: https://www.gnu.org/software/bash/
[Docker-badge]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[Nginx-badge]: https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white
[Nginx-url]: https://nginx.org/
