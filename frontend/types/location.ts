export interface OfficeLocation {
  id: number
  name: string
  latitude: number
  longitude: number
  radius_meters: number
  is_active: boolean
}

export interface GeofenceSetting {
  enabled: boolean
}
