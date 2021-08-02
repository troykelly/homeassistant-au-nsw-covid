# NSW Covid Cases

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE.md)

[![hacs][hacsbadge]](hacs)
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Covid cases and vaccination data from NSW Health_


## Installation

1. Using HACS add the repository `https://github.com/troykelly/homeassistant-au-nsw-covid`.
1. Add the integration
1. Restart Home Assistant
1. In `Integrations` add the `NSW Covid` integration
   - In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "NSW Covid"

## Note

This is a screen scraper. That is not allowed in Home Assistant.

There just is no other way to get this data.

## Usage

This will create a series of sensors with current NSW Health Covid data.

Keep in mind - NSW Health manually updates their website, when they please.
Aunty Gladys does her briefing at 11am, and sometimes the page is not
updated until late in the afternoon.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[readme]: https://github.com/troykelly/homeassistant-au-nsw-covid
[buymecoffee]: https://www.buymeacoffee.com/troykelly
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/troykelly/homeassistant-au-nsw-covid.svg?style=for-the-badge
[commits]: https://github.com/troykelly/homeassistant-au-nsw-covid/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/troykelly/homeassistant-au-nsw-covid.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Troy%20Kelly%20%40troykelly-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/troykelly/homeassistant-au-nsw-covid.svg?style=for-the-badge
[releases]: https://github.com/troykelly/homeassistant-au-nsw-covid/releases