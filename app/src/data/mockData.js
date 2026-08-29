export const floats = [
    {
      id: "2901234",
      latitude: 12.3,
      longitude: 73.2,
      region: "Arabian Sea",
      status: "Active",
      latestReading: 27.3,
      maxDepth: 2000,
      features: ["Temp", "Salinity", "Oxygen"],
    },
    {
      id: "2901240",
      latitude: 15.8,
      longitude: 86.4,
      region: "Bay of Bengal",
      status: "Active",
      latestReading: 26.1,
      maxDepth: 1500,
      features: ["Temp", "Salinity"],
    },
    {
      id: "2901266",
      latitude: 8.4,
      longitude: 62.1,
      region: "Arabian Sea",
      status: "Inactive",
      latestReading: 28.0,
      maxDepth: 1000,
      features: ["Temp", "Chlorophyll"],
    },
    {
      id: "2901278",
      latitude: 5.2,
      longitude: 72.5,
      region: "Indian Ocean (Equatorial)",
      status: "Active",
      latestReading: 25.4,
      maxDepth: 1800,
      features: ["Temp", "Oxygen"],
    },
    {
      id: "2901288",
      latitude: -45.0,
      longitude: 80.0,
      region: "Southern Ocean",
      status: "Active",
      latestReading: 8.4,
      maxDepth: 2000,
      features: ["Temp", "Salinity"],
    },
  ];
  export const profiles = {
  "2901234": {
    depth: [0, 100, 500, 1000, 1500],
    temperature: [28.1, 24.5, 18.2, 9.4, 4.8],
    salinity: [35.2, 35.4, 35.6, 35.0, 34.8],
  },

  "2901240": {
    depth: [0, 100, 500, 1000, 1500],
    temperature: [26.8, 23.9, 17.5, 8.8, 4.5],
    salinity: [35.0, 35.2, 35.5, 34.9, 34.7],
  },
};

export const timeSeries = {
  months: ["Mar", "Apr", "May", "Jun", "Jul", "Aug"],

  "2901234": [27.0, 27.5, 28.1, 27.8, 28.3, 27.3],

  "2901240": [26.1, 26.4, 26.8, 26.5, 26.9, 26.8],
};
