
# NSW COVID-19 Case & Vacination Data for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE.md)
[![CodeQL][codeqlbadge]][codeql]

[![hacs][hacsbadge]](hacs)
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Covid cases and vaccination data sourced directly from New South Wales Health_

<img width="503" alt="NSW Covid Stats for Home Assistant" src="https://user-images.githubusercontent.com/4564803/127966191-337817de-a656-438e-b53e-3ba79d2a23cd.png">

<img width="467" alt="NSW Health Covid Sensors" src="https://user-images.githubusercontent.com/4564803/127804075-05ee9641-ed7b-45f0-98ac-5d833538cb37.png">

Track daily changes in the New South Wales health districts.

Visibility in to cases, vaccinations and sources. Sourced directly from NSW Health.

## Note

This is not affiliated with, nor approved by NSW Health.

Data is sourced by screen scraping - as NSW Health does not provide this information in any other format.

## Installation

1. Using HACS add the repository `https://github.com/troykelly/homeassistant-au-nsw-covid`.
1. Add the integration
1. Restart Home Assistant
1. In `Integrations` add the `NSW Covid` integration
   - In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "NSW Covid"

## Note

This is a screen scraper. That is not allowed in Home Assistant.

There just is no other way to get this data.

### Missing Information

One number that would be great to have is "cases in community" especially in the last 24 hours.

NSW Health does not publish this number. In a press conference, it was stated that the number is too fluid.

If you have a source of extra information that you would like to see - create an issue!

## Usage

This will create a series of sensors with current NSW Health Covid data.

Keep in mind - NSW Health manually updates their website, when they please.
Aunty Gladys does her briefing at 11am, and sometimes the page is not
updated until late in the afternoon.

## Template Sensors

Some numbers are derived from the data. You can calculate these as a template sensor.

### Local Cases (all of NSW)

A calculation of `total cases` - the sum of `interstate` and `overseas`

```yaml
template:
   - sensor:
       - name: "Covid NSW Last 24 Hours State"
         unique_id: "covid_nsw_last_24_hours_state"
         icon: "mdi:virus"
         unit_of_measurement: "cases"
         state: >
           {% set total = states('sensor.covid_nsw_last_24_hours_total') | int %}
           {% set overseas = states('sensor.covid_nsw_last_24_hours_overseas_source') | int %}
           {% set interstate = states('sensor.covid_nsw_last_24_hours_interstate_source') | int %}
           {% set out_of_state = (overseas + interstate) %}
           {{ (total - out_of_state) }}
         attributes:
           attribution: >
             {{ state_attr('sensor.covid_nsw_last_24_hours_total', 'attribution') }}
           published: >
             {{ state_attr('sensor.covid_nsw_last_24_hours_total', 'published') }}
```

### Vaccination Rate

Percentage of NSW population who've had second dose.

Assuming population is `6565651`

```yaml
template:
   - sensor:
       - name: "Covid NSW Fully Vaccinated"
         unique_id: "covid_nsw_state_vaccination_rate"
         icon: "mdi:needle"
         unit_of_measurement: "%"
         state: >
           {% set total_population = 6565651 %}
           {% set half_dose_total = (states('sensor.covid_nsw_doses') | int) / 2 %}
           {% set state_second_dose_vaccinated_total = half_dose_total / total_population %}
           {{ (state_second_dose_vaccinated_total * 100)|round(2, 'floor') }}
         attributes:
           attribution: >
             {{ state_attr('sensor.covid_nsw_doses', 'attribution') }}
           published: >
             {{ state_attr('sensor.covid_nsw_doses', 'gp_network_doses_updated') }}
           first_dose: >
             {% set total_population = 6565651 %}
             {% set first_dose_total = states('sensor.covid_nsw_total_first_dose_vaccine') | int %}
             {% set state_first_dose_vaccinated_total = first_dose_total / total_population %}
             {{ (state_first_dose_vaccinated_total * 100)|round(2, 'floor') }}
           first_dose_last_24_hours: >
             {% set total_population = 6565651 %}
             {% set first_dose_last24 = states('sensor.covid_nsw_last_24_hours_first_dose_vaccine') | int %}
             {% set state_first_dose_vaccinated_last24 = first_dose_last24 / total_population %}
             {{ (state_first_dose_vaccinated_last24 * 100)|round(6, 'floor') }}
           second_dose: >
             {% set total_population = 6565651 %}
             {% set second_dose_total = states('sensor.covid_nsw_total_second_dose_vaccine') | int %}
             {% set state_second_dose_vaccinated_total = second_dose_total / total_population %}
             {{ (state_second_dose_vaccinated_total * 100)|round(2, 'floor') }}
           second_dose_last_24_hours: >
             {% set total_population = 6565651 %}
             {% set second_dose_last24 = states('sensor.covid_nsw_last_24_hours_second_dose_vaccine') | int %}
             {% set state_second_dose_vaccinated_last24 = second_dose_last24 / total_population %}
             {{ (state_second_dose_vaccinated_last24 * 100)|round(6, 'floor') }}
           last_24_hours: >
             {% set total_population = 6565651 %}
             {% set second_dose_last24 = states('sensor.covid_nsw_last_24_hours_second_dose_vaccine') | int %}
             {% set state_second_dose_vaccinated_last24 = second_dose_last24 / total_population %}
             {{ (state_second_dose_vaccinated_last24 * 100)|round(6, 'floor') }}
```

## Data Attribution

© State of New South Wales NSW Ministry of Health. For current information go to www.health.nsw.gov.au

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
[codeqlbadge]: https://github.com/troykelly/homeassistant-au-nsw-covid/actions/workflows/codeql-analysis.yml/badge.svg?branch=main&style=for-the-badge
[codeql]: https://github.com/troykelly/homeassistant-au-nsw-covid/actions/workflows/codeql-analysis.yml
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/troykelly/homeassistant-au-nsw-covid.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Troy%20Kelly%20%40troykelly-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/troykelly/homeassistant-au-nsw-covid.svg?style=for-the-badge
[releases]: https://github.com/troykelly/homeassistant-au-nsw-covid/releases
