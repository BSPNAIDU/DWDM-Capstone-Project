# ============================================================
# AGRICULTURAL SOLID WASTE MANAGEMENT
# Rule-based module - No dataset required
# ============================================================

WASTE_TYPES = {

    "Crop Residues": {
        "examples": "Straw, stalks, leaves, husks",
        "category": "Organic",
        "treatment": "Composting / Biochar Production",
        "output": "Compost / Biochar",
        "utilization": "Agricultural Use",
        "method": "Composting",
        "recovery_rate": 0.75,
        "description": "Crop residues can be converted into compost or biochar instead of being openly burned."
    },

    "Fruit & Vegetable Waste": {
        "examples": "Peels, rotten produce, market waste",
        "category": "Organic",
        "treatment": "Composting / Biogas Production",
        "output": "Compost / Biogas",
        "utilization": "Agricultural Use / Energy Generation",
        "method": "Composting",
        "recovery_rate": 0.80,
        "description": "Organic fruit and vegetable waste is suitable for composting and anaerobic digestion."
    },

    "Animal & Farm Waste": {
        "examples": "Cow dung, poultry litter, manure",
        "category": "Organic",
        "treatment": "Biogas Production / Composting",
        "output": "Biogas / Organic Fertilizer",
        "utilization": "Energy Generation / Agricultural Use",
        "method": "Biogas Production",
        "recovery_rate": 0.85,
        "description": "Animal waste can be processed through anaerobic digestion to produce biogas and digestate."
    },

    "Agro-Processing Waste": {
        "examples": "Hulls, bagasse, seed waste",
        "category": "Organic",
        "treatment": "Composting / Thermal Conversion",
        "output": "Compost / Biochar / Bio-oil",
        "utilization": "Agricultural Use / Industrial Use",
        "method": "Thermal Conversion",
        "recovery_rate": 0.70,
        "description": "Processing residues can be converted into useful agricultural or energy products."
    },

    "Agricultural Plastic Waste": {
        "examples": "Mulching sheets, bags, drip materials",
        "category": "Recyclable",
        "treatment": "Recycling",
        "output": "Recycled Plastic Materials",
        "utilization": "Industrial Use",
        "method": "Recycling",
        "recovery_rate": 0.65,
        "description": "Agricultural plastics should be collected separately and sent to authorized recycling facilities."
    },

    "Hazardous Farm Waste": {
        "examples": "Pesticide containers, fertilizer bags, chemical containers",
        "category": "Hazardous",
        "treatment": "Safe Treatment & Disposal",
        "output": "Safely Disposed Waste",
        "utilization": "Environmental Protection",
        "method": "Safe Disposal",
        "recovery_rate": 0.10,
        "description": "Hazardous agricultural waste requires controlled collection and disposal through authorized facilities."
    }
}


def manage_solid_waste(waste_type, quantity):

    if waste_type not in WASTE_TYPES:
        raise ValueError("Invalid agricultural waste type.")

    quantity = float(quantity)

    if quantity <= 0:
        raise ValueError("Waste quantity must be greater than zero.")

    data = WASTE_TYPES[waste_type]

    recovery_quantity = quantity * data["recovery_rate"]
    remaining_quantity = quantity - recovery_quantity

    category = data["category"]

    if category == "Organic":
        segregation = "Place in Organic Waste Collection"
    elif category == "Recyclable":
        segregation = "Place in Recyclable Waste Collection"
    else:
        segregation = "Place in Hazardous Waste Collection"

    if category == "Hazardous":
        priority = "HIGH"
        environmental_risk = "High"
    elif category == "Organic":
        priority = "MEDIUM"
        environmental_risk = "Low"
    else:
        priority = "MEDIUM"
        environmental_risk = "Moderate"

    return {
        "success": True,
        "waste_type": waste_type,
        "quantity_kg": round(quantity, 2),
        "category": category,
        "examples": data["examples"],
        "segregation": segregation,
        "treatment": data["treatment"],
        "method": data["method"],
        "output": data["output"],
        "utilization": data["utilization"],
        "recovery_rate": round(data["recovery_rate"] * 100, 2),
        "recoverable_quantity_kg": round(recovery_quantity, 2),
        "remaining_quantity_kg": round(remaining_quantity, 2),
        "priority": priority,
        "environmental_risk": environmental_risk,
        "description": data["description"]
    }


def get_waste_types():
    return list(WASTE_TYPES.keys())