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