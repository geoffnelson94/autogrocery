import pint
from sugarcube import *

def CheckForAmountRange(amount):
    if ("-" in amount):
        return True
    else:
        return False

def AddSameIngredients(item, newIngredient, categoryList):
    for idx, addedIngredient in enumerate(categoryList):
        if item in addedIngredient:
            oldIdx = idx
            oldAmountStr = addedIngredient.split(' ')[0]
            oldAmount = GetQuantity(addedIngredient)
            oldMeasureType = IdentifyMeasurementType(addedIngredient)
            break
        
    newAmount = GetQuantity(newIngredient)
    newMeasureType = IdentifyMeasurementType(newIngredient)
    
    if (oldMeasureType == newMeasureType):
        if (isinstance(oldAmount, list) or isinstance(newAmount, list)):
            print("deal with ranges...", "\n(", newIngredient, ")", "\nvs.\n" "(", categoryList[idx], ")")
            return False
        else:
            total = float(oldAmount) + float(newAmount)
            oldItem = categoryList[oldIdx]
            categoryList[oldIdx] = categoryList[oldIdx].replace(oldAmountStr, "")
            categoryList[oldIdx] = str(total) + categoryList[oldIdx]
    else:
        print("Unrecognized measurement comparison! (", oldMeasureType, "/", newMeasureType, ")",
              "\n(", newIngredient, ")", "\nvs.\n" "(", categoryList[idx], ")")
        return False
    return True
def ConvertToDecimal(quantity):
    if isinstance(quantity,list):
        for x in quantity:
            if "/" in x:
                float(x.split('/')[0]) / float(x.split('/').split(' ')[1])
    else:
        quantity = float(quantity.split('/')[0]) / float(quantity.split('/')[1].split(' ')[0])
        
    return str(quantity)

def GetQuantity(item):
    quantity = item.split(' ')[0]
    if CheckForAmountRange(quantity):
        quantity = quantity.split("-")
    # Deal with "/" instead of decimal places
    if "/" in quantity:
        quantity = ConvertToDecimal(quantity)
    
    return quantity

def IdentifyMeasurementType(item):
    ureg = pint.UnitRegistry()
    measurementType = item.split(' ')[1]
    
    uselessDescriptors = ["SMALL", "MEDIUM", "LARGE"]
    # Check for descriptors
    if measurementType in uselessDescriptors:
        measurementType = item.split(' ')[2]
    # Remove stray ","
    measurementType = measurementType.replace(",", "")
    
    match measurementType:
        case "TABLESPOON" | "TABLESPOONS":
            return Volume.tablespoon
        case "OUNCE" | "OUNCES":
            return Mass.ounce
        case "CUP" | "CUPS":
            return Volume.cup
        case _:
            return measurementType
        
def SetupSugarCube():
    # Common cooking measures

    Mass = Measure('Mass', Unit('gram', 'g'))
    Mass.addUnits(SIUnitsFromUnit(Mass.gram))

    Volume = Measure('Volume', Unit('liter', 'l'))
    Volume.addUnits(SIUnitsFromUnit(Volume.liter))

    Temperature = Measure('Temperature', Unit('celsius', '°C'))
    Temperature.addUnits([
        Unit('kelvin',      '°K',           converter=Converter.Constant(-273.15)),
        Unit('fahrenheit',  '°F',           converter=Converter.Linear(1.8, 32).reverse),
        Unit('thermostat',  'thermostat',   converter=Converter.Linear(30), preFix=True)
    ])

    # other measures

    Length = Measure('Length', Unit('meter', 'm'))
    Length.addUnits(SIUnitsFromUnit(Length.meter))

    Time = Measure('Time', Unit('second', 's'))
    Time.addUnits([
        Unit('minute', 'min', converter=Converter.Linear(60)),
        Unit('hour', 'h', converter=Converter.Linear(3600))
    ])

    # measure conversion

    milliliter = Volume.milliliter
    gram = Mass.gram

    Volume.addTransform(Mass, lambda volume, element: (element.density * volume.to(milliliter)).value * gram)
    Mass.addTransform(Volume, lambda mass, element: ((mass.to(gram)).value / element.density) * milliliter)

    # USA cooking units

    CUP_IN_LITER    = 0.240         # 'US legal' cup definition
    GALLON_IN_LITER = 231 * 2.54**3 # 231 cubic inches
    POUND_IN_GRAMS  = 453.59237     # NIST pound definition

    Volume.addUnits([
        # FDA units
        Unit('pinch',           'pinch',    converter=Converter.Linear(CUP_IN_LITER / 768)),
        Unit('teaspoon',        'tsp.',     converter=Converter.Linear(CUP_IN_LITER / 48)),
        Unit('tablespoon',      'tbsp.',    converter=Converter.Linear(CUP_IN_LITER / 16)),
        Unit('fluidOunce',      'fl. oz.',  converter=Converter.Linear(CUP_IN_LITER / 8)),
        Unit('cup',             'cup',      converter=Converter.Linear(CUP_IN_LITER)),

        #other units
        Unit('pint',            'pt.',      converter=Converter.Linear(GALLON_IN_LITER / 8)),
        Unit('quart',           'qt',       converter=Converter.Linear(GALLON_IN_LITER / 4)),
        Unit('gallon',          'gal.',     converter=Converter.Linear(GALLON_IN_LITER))
    ])

    Mass.addUnits([
        Unit('ounce',   'oz',       converter=Converter.Linear(POUND_IN_GRAMS / 16)),
        Unit('stick',   'stick',    converter=Converter.Linear(POUND_IN_GRAMS / 4)),
        Unit('pound',   'lb',       converter=Converter.Linear(POUND_IN_GRAMS))
    ])
            