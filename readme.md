### Processing Rule 1

Transform cost codes into a hierarchical structure following these exact rules for processing:

1. First group all entries by building. Each building must contain only unique floor entries.

2. For each line:
- Split on comma for hours
- Split remaining on "-" for description
- Split remaining on spaces for codes
- Group under building first, then floor, then area


3. Required hierarchy levels:
Building level names:
- B1 = "Building 1 North"
- B2 = "Building 2 South"
- B3 = "Building 3"
- B4 = "Building 4"
- GC = "General Conditions"


Floor level names:
- F01-F04 = "Floor {nn}"
- F05 = "Roof"
- F0 = "Phase 0"
- F1 = "1st Floor"
- F2 = "2nd Floor"
- F3 = "Roof"

Area level names:
- A0 = "General Conditions"
- AA = "Area A"
- AB = "Area B"
- AC = "Area C"
- AD = "Area D"
- AE = "Area A Exterior"
- AF = "Area B Exterior"
- AG = "Area C Exterior"
- AH = "Area D Exterior"
- AK = "Ceilings"
- Int = "Interior"
- Ext = "Exterior"

4. Processing requirements:
- Each floor code must appear EXACTLY ONCE per building
- Combine all matching floor items under single floor entry
- Remove redundant text from descriptions
- Keep cost codes as prefixes
- Convert all hours to numbers
- Preserve original codes in fullCode field
- Sort all entries for consistency

5. Required output structure:
[
    {
        "label": "Building 2 South",
        "children": [
            {
                "label": "Floor 01", // Each floor appears ONCE
                "children": [
                    {
                        "label": "Area C",
                        "children": [
                            {
                                "label": "5400 - Ext Frame",
                                "hours": 44,
                                "fullCode": "original code string"
                            }
                        ]
                    }
                ]
            }
        ]
    }
]


6. Example transformation:
Input:
B2 F01 AC 5400 - S FL 01 Area C Int Ext Frame,44
B2 F01 AD 5400 - S FL 01 Area D Int Ext Frame,23


Building 2 South, Floor 01, Area C, 5400 - Ext Frame, 44, B2 F01 AC 5400 - S FL 01 Area C Int Ext Frame
Building 2 South, Floor 01, Area D, 5400 - Ext Frame, 23, B2 F01 AD 5400 - S FL 01 Area D Int Ext Frame


Must produce:
[
    {
        "label": "Building 2 South",
        "children": [
            {
                "label": "Floor 01",
                "children": [
                    {
                        "label": "Area C",
                        "children": [
                            {
                                "label": "5400 - Ext Frame",
                                "hours": 44,
                                "fullCode": "B2 F01 AC 5400 - S FL 01 Area C Int Ext Frame"
                            }
                        ]
                    },
                    {
                        "label": "Area D",
                        "children": [
                            {
                                "label": "5400 - Ext Frame",
                                "hours": 23,
                                "fullCode": "B2 F01 AD 5400 - S FL 01 Area D Int Ext Frame"
                            }
                        ]
                    }
                ]
            }
        ]
    }
]



Critical rules:
1. Use Map to collect all items before creating structure
2. Create floor entries ONLY from unique floor codes
3. Never duplicate floor entries
4. Combine all items under correct unique floor
5. Validate structure before return
6. Error if duplicates found


Process all input using these rules. Return properly formatted JSON with guaranteed unique floors per building.


### Processing Rule 2



Transform preprocessed cost code data into a hierarchical JSON structure. The input data has these columns:
build,floor,area,hour,full,label
1. DATA STRUCTURE
Input format:
- build: Building name (e.g., "Building 1 North")
- floor: Floor name (e.g., "Floor 01")
- area: Area name (e.g., "Area A")
- hour: Hours as number
- full: Original full code
- label: Work description
2. PROCESSING RULES
- Each building appears once as a primary node
- Each floor appears once per building
- Areas are grouped under floors
- Work items are grouped under areas
- Use Set for uniqueness at each level
- Map for collecting items
3. REQUIRED OUTPUT STRUCTURE
```json
[
  {
    "label": "Building Name",
    "children": [
      {
        "label": "Floor Name",     // EXACTLY once per building
        "children": [
          {
            "label": "Area Name",
            "children": [
              {
                "label": "Work Description",
                "hours": number,
                "fullCode": "Original Code"
              }
            ]
          }
        ]
      }
    ]
  }
]
```
4. PROCESSING STEPS
```javascript
function processStructuredData(rows) {
  // Primary storage
  const buildingMap = new Map();
  const floorSets = new Map();
  // First pass - collect unique floors per building
  rows.forEach(row => {
    const {build, floor} = row;
    if (!floorSets.has(build)) {
      floorSets.set(build, new Set());
    }
    if (floor) {
      floorSets.get(build).add(floor);
    }
  });
  // Second pass - build structure
  rows.forEach(row => {
    const {build, floor, area, hour, full, label} = row;
    if (!buildingMap.has(build)) {
      buildingMap.set(build, {
        label: build,
        children: []
      });
    }
    const buildingNode = buildingMap.get(build);
    // Find or create floor
    let floorNode = buildingNode.children.find(f => f.label === floor);
    if (!floorNode && floor) {
      floorNode = {
        label: floor,
        children: []
      };
      buildingNode.children.push(floorNode);
    }
    // Find or create area
    if (floor && area) {
      let areaNode = floorNode.children.find(a => a.label === area);
      if (!areaNode) {
        areaNode = {
          label: area,
          children: []
        };
        floorNode.children.push(areaNode);
      }
      // Add work item
      areaNode.children.push({
        label: label,
        hours: parseInt(hour),
        fullCode: full
      });
    } else if (!floor) {
      // Handle items without floor/area (e.g., General Conditions)
      buildingNode.children.push({
        label: label,
        hours: parseInt(hour),
        fullCode: full
      });
    }
  });
  return Array.from(buildingMap.values());
}
```
5. VALIDATION
```javascript
function validateStructure(result) {
  result.forEach(building => {
    const floorLabels = new Set();
    building.children.forEach(floor => {
      // Skip validation for leaf nodes (e.g., General Conditions)
      if (!floor.children) return;
      if (floorLabels.has(floor.label)) {
        throw new Error(`Duplicate floor ${floor.label} in ${building.label}`);
      }
      floorLabels.add(floor.label);
    });
  });
  return result;
}
```
6. EXAMPLE
Input:
```
build,floor,area,hour,full,label
Building 1 North,Floor 01,Area A,12,B1 F01 AA 5400 - N FL 01 Area A Int Ext Frame,Ext Frame
Building 1 North,Floor 01,Area B,10,B1 F01 AB 5400 - N FL 01 Area B Int Ext Frame,Ext Frame
```
Output:
```json
[
  {
    "label": "Building 1 North",
    "children": [
      {
        "label": "Floor 01",
        "children": [
          {
            "label": "Area A",
            "children": [
              {
                "label": "Ext Frame",
                "hours": 12,
                "fullCode": "B1 F01 AA 5400 - N FL 01 Area A Int Ext Frame"
              }
            ]
          },
          {
            "label": "Area B",
            "children": [
              {
                "label": "Ext Frame",
                "hours": 10,
                "fullCode": "B1 F01 AB 5400 - N FL 01 Area B Int Ext Frame"
              }
            ]
          }
        ]
      }
    ]
  }
]
```
7. CRITICAL RULES
- Use Map/Set for all grouping
- Process rows in order
- Maintain hierarchy integrity
- Guarantee unique floors
- Handle special cases (General Conditions)
- Preserve all data
Return properly formatted JSON with guaranteed unique entries at each level.