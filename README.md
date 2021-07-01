# Home Assistant Augsburg COVID-19 Tracker Integration

## Adding to your dashboard

You can add an overview of the current infection numbers to your dashboard using the [multiple-entity-row](https://github.com/benct/lovelace-multiple-entity-row) card:

```yaml
type: entities
entities:
  - type: custom:multiple-entity-row
    entity: sensor.coronavirus_augsburg
    entities:
      - attribute: total_cases
        name: Cases
      - attribute: num_dead
        name: Deaths
      - attribute: num_recovered
        name: Recovered
      - attribute: num_infected
        name: Infected
    show_state: false
    icon: mdi:biohazard
    name: COVID-19
    secondary_info:
      attribute: incidence
      unit: cases/100k
```
