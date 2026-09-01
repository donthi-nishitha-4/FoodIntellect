import os

CORPUS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'food_corpus'))
os.makedirs(CORPUS_DIR, exist_ok=True)

documents = {
    "lecithin.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Lecithin
Category: Emulsifier / Phospholipid
Function: Emulsification, texture improvement, moisture retention.
Description: Lecithin is a natural fatty substance found in plant and animal tissues, most commonly extracted from soybeans, sunflower seeds, or egg yolks. It is widely used in chocolate, margarine, baked goods, and infant formula to blend oil and water components smoothly.
Allergen Information: May be derived from Soy or Eggs. Soy lecithin requires allergen disclosure in standard labeling if derived from unrefined soy oil.
Dietary Considerations: Vegan when derived from Soy or Sunflower; Vegetarian.
Health Effects & Notes: Generally Recognized As Safe (GRAS) by FDA and EFSA. Supports brain health as a source of choline.""",

    "soy_lecithin.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Soy Lecithin
Category: Emulsifier
Function: Prevents crystallization, stabilizes emulsions, reduces viscosity in chocolate.
Description: Soy lecithin is a byproduct of soybean oil processing. In chocolate manufacturing, adding 0.3% to 0.5% soy lecithin reduces cocoa butter requirements while maintaining flowability and smooth mouthfeel.
Allergen Information: Allergen Warning - Contains Soy (for individuals with severe soybean protein allergy, highly refined soy lecithin usually contains negligible protein).
Dietary Considerations: Vegan, Halal, Kosher. Non-GMO variants exist.
Health Effects & Notes: Widely accepted food additive (E322) used across processed foods.""",

    "sodium_benzoate.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Sodium Benzoate
Category: Preservative / Antimicrobial
Function: Inhibits growth of mold, yeast, and bacteria in acidic food products.
Description: Sodium benzoate is the sodium salt of benzoic acid. It is most effective in acidic environments (pH below 4.5) and is commonly added to carbonated beverages, fruit juices, pickles, salad dressings, and condiments.
Allergen Information: Non-allergenic.
Dietary Considerations: Vegan, Vegetarian, Kosher.
Health Effects & Notes: Designated as E211. When combined with Vitamin C (Ascorbic Acid) under heat and light, it can form trace amounts of benzene. Controlled strictly below NFR safety limits.""",

    "potassium_sorbate.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Potassium Sorbate
Category: Preservative / Antifungal
Function: Prevents mold and yeast spoilage in food and wine.
Description: Potassium sorbate is the potassium salt of sorbic acid. It works by inactivating fungal enzymes. It is widely used in cheese, wine, yogurt, dried fruit, baked goods, and syrups without altering flavor profiles.
Allergen Information: Non-allergenic.
Dietary Considerations: Vegan, Vegetarian.
Health Effects & Notes: E202. Recognized as safe with minimal toxicity when consumed within ADI limits.""",

    "citric_acid.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Citric Acid
Category: Acidulant / Flavor Enhancer / Antioxidant
Function: Provides sour taste, regulates pH acidity, acts as a natural preservative and chelating agent.
Description: Citric acid is a weak organic acid found naturally in citrus fruits like lemons and limes. Commercially, it is produced by fermentation using Aspergillus niger mold on sugar sources. It is used in soft drinks, candies, jams, and canned foods.
Allergen Information: Non-allergenic (mold proteins are filtered out in commercial processing).
Dietary Considerations: Vegan, Vegetarian.
Health Effects & Notes: E330. Essential intermediate in the Krebs citric acid cycle in human metabolism.""",

    "ascorbic_acid.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Ascorbic Acid (Vitamin C)
Category: Antioxidant / Nutrient / Flour Improver
Function: Prevents oxidation and browning, fortifies food with Vitamin C, strengthens bread dough gluten network.
Description: Ascorbic acid is a water-soluble essential vitamin and potent antioxidant. It is added to fruit juices, cured meats (to prevent nitrosamine formation), and commercial bread baking.
Allergen Information: Non-allergenic.
Dietary Considerations: Vegan, Vegetarian.
Health Effects & Notes: E300. Essential human micronutrient preventing scurvy and supporting immune function.""",

    "high_fructose_corn_syrup.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: High Fructose Corn Syrup (HFCS)
Category: Sweetener / Carbohydrate
Function: Sweetening agent, browning enhancer, humectant for baked goods.
Description: HFCS is produced from corn starch that has been processed by glucose isomerase to convert a portion of its glucose into fructose. HFCS-55 (55% fructose, 42% glucose) has sweetening parity with liquid sucrose and is heavily used in sodas, cereals, and processed snacks.
Allergen Information: Corn-derived. Low risk for corn allergy.
Dietary Considerations: Vegan, Vegetarian.
Health Effects & Notes: High intake is strongly linked to obesity, metabolic syndrome, non-alcoholic fatty liver disease, and type-2 diabetes due to rapid hepatic fructose processing.""",

    "maltodextrin.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Maltodextrin
Category: Thickener / Bulking Agent / Carbohydrate
Function: Improves texture, adds volume without intense sweetness, serves as a carrier for flavors and spice mixes.
Description: Maltodextrin is a polysaccharide produced from vegetable starch (corn, wheat, tapioca, or potato) by partial hydrolysis. It digests rapidly and has a high glycemic index (GI 85-105).
Allergen Information: If derived from wheat, it must disclose wheat source in some jurisdictions, though it is usually gluten-free.
Dietary Considerations: Vegan, Vegetarian.
Health Effects & Notes: Rapidly spikes blood glucose levels; caution recommended for individuals with diabetes.""",

    "stevia.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Stevia (Steviol Glycosides)
Category: Zero-Calorie Natural Sweetener
Function: High-intensity natural sweetener (200-300x sweeter than sucrose).
Description: Extracted from the leaves of the Stevia rebaudiana plant. Rebaudioside A (Reb A) is the sweetest component with minimal liquorice-like bitter aftertaste. Used in sugar-free drinks, teas, yogurts, and keto products.
Allergen Information: Non-allergenic.
Dietary Considerations: Vegan, Diabetic-friendly, Keto-friendly, Zero-Calorie.
Health Effects & Notes: E960. Does not impact blood glucose or insulin levels.""",

    "aspartame.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Aspartame
Category: Artificial Sweetener
Function: Intense sweetening agent (~200x sweeter than sugar) with low caloric value.
Description: Aspartame is a methyl ester of a dipeptide composed of L-aspartic acid and L-phenylalanine. Used extensively in diet sodas, sugar-free chewing gum, and low-calorie desserts.
Allergen Information: Warning required for Individuals with Phenylketonuria (PKU).
Dietary Considerations: Vegetarian, Low-calorie.
Health Effects & Notes: E951. Metabolized into aspartic acid, phenylalanine, and methanol. Must be avoided by individuals with PKU due to inability to metabolize phenylalanine.""",

    "erythritol.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Erythritol
Category: Sugar Alcohol (Polyol) / Sweetener
Function: Bulk sweetener (~70% sweet as sugar) with zero net calories and cooling mouthfeel.
Description: Erythritol is a 4-carbon sugar alcohol produced naturally by yeast fermentation of corn glucose. It is absorbed in the small intestine and excreted unchanged in urine, avoiding digestive distress common with other polyols like sorbitol.
Allergen Information: Non-allergenic.
Dietary Considerations: Vegan, Keto-friendly, Diabetic-safe, Non-cariogenic (does not cause tooth decay).
Health Effects & Notes: E968. Highest digestive tolerance among all sugar alcohols.""",

    "xanthan_gum.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Xanthan Gum
Category: Thickener / Stabilizer / Hydrocolloid
Function: Increases liquid viscosity, prevents phase separation, provides gluten-free dough elasticity.
Description: Produced by aerobic fermentation of glucose or sucrose by Xanthomonas campestris bacteria. Widely used in salad dressings, gluten-free baking, sauces, and ice creams.
Allergen Information: Produced using corn, soy, or wheat substrate; minimal residual protein.
Dietary Considerations: Vegan, Vegetarian, Gluten-free essential ingredient.
Health Effects & Notes: E415. Soluble dietary fiber; safe at normal consumption levels.""",

    "guar_gum.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Guar Gum
Category: Thickener / Emulsifier
Function: Viscosity enhancement, ice crystal growth inhibition in frozen desserts.
Description: Milled endosperm of guar beans (Cyamopsis tetragonoloba). Has 8x the thickening power of cornstarch. Found in ice creams, sauces, plant milks, and gluten-free flours.
Allergen Information: Legume family; rare cross-reactivity with soy or peanut allergies.
Dietary Considerations: Vegan, Vegetarian.
Health Effects & Notes: E412. Dietary fiber that slows carbohydrate absorption.""",

    "pectin.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Pectin
Category: Gelling Agent / Thickener
Function: Forms heat-reversible gels in high-sugar acidic environments.
Description: Structural heteropolysaccharide extracted from citrus peels or apple pomace. Primary gelling ingredient in fruit jams, jellies, marmalades, and gummy confections.
Allergen Information: Non-allergenic.
Dietary Considerations: Vegan gelatin alternative, Vegetarian, Kosher.
Health Effects & Notes: E440. Soluble fiber beneficial for gut motility.""",

    "carrageenan.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Carrageenan
Category: Stabilizer / Gelling Agent
Function: Binds proteins in dairy products, prevents whey separation in chocolate milk and ice cream.
Description: Family of natural linear sulfated polysaccharides extracted from red edible seaweeds (Irish moss). Highly effective at stabilizing milk proteins (casein).
Allergen Information: Seaweed-derived; non-allergenic.
Dietary Considerations: Vegan, Vegetarian.
Health Effects & Notes: E407. Food-grade degraded carrageenan is restricted due to potential gastrointestinal inflammation concerns in high doses.""",

    "gelatin.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Gelatin
Category: Gelling Agent / Thickener / Clarifier
Function: Thermoreversible gelation, foaming, mouthfeel enhancer in gummies and marshmallows.
Description: Protein substance derived by partial hydrolysis of collagen extracted from animal skin, bones, and connective tissue (pork, beef, or fish).
Allergen Information: Animal protein; fish gelatin requires fish allergen labeling.
Dietary Considerations: NOT VEGAN / NOT VEGETARIAN. Requires Halal/Kosher certification (Beef/Fish derived).
Health Effects & Notes: Rich in amino acids glycine and proline.""",

    "milk_powder.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Milk Powder (Skimmed Milk Powder / Whole Milk Powder)
Category: Dairy Ingredient / Protein Source
Function: Provides dairy flavor, browning (Maillard reaction), protein enrichment, and emulsion.
Description: Dehydrated milk manufactured by spray drying pasteurized cow's milk. Contains milk proteins (casein, whey), lactose sugar, and dairy minerals.
Allergen Information: MAJOR ALLERGEN - Contains Milk & Lactose.
Dietary Considerations: Vegetarian; NOT VEGAN.
Health Effects & Notes: Rich source of calcium and high-quality complete protein.""",

    "whey_protein.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Whey Protein Concentrate (WPC)
Category: Dairy Protein / Emulsifier
Function: Protein fortification, gel formation, water binding in sports nutrition and bakery.
Description: Co-product of cheese manufacturing, isolated from liquid whey. WPC-80 contains 80% protein with small amounts of dairy fat and lactose.
Allergen Information: MAJOR ALLERGEN - Contains Milk (Whey Protein & Lactose).
Dietary Considerations: Vegetarian; NOT VEGAN.
Health Effects & Notes: High biological value protein rich in branched-chain amino acids (BCAAs) like leucine.""",

    "palm_oil.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Palm Oil / Palm Olein
Category: Fat / Vegetable Oil
Function: Provides solid fat structure at room temperature without hydrogenation (trans-fat free).
Description: Edible vegetable oil derived from the mesocarp of the fruit of oil palms (Elaeis guineensis). Used in shortenings, margarines, biscuits, instant noodles, and chocolate spreads.
Allergen Information: Non-allergenic.
Dietary Considerations: Vegan, Vegetarian.
Health Effects & Notes: High saturated fatty acid content (~50% palmitic acid); environmental sustainability concerns regarding deforestation.""",

    "msg.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Monosodium Glutamate (MSG)
Category: Flavor Enhancer / Umami Agent
Function: Enhances savory umami flavor profile, reduces required sodium level by up to 30%.
Description: Sodium salt of glutamic acid, an abundant non-essential amino acid. Produced commercially by bacterial fermentation of sugar beet, sugar cane, or corn molasses.
Allergen Information: Non-allergenic.
Dietary Considerations: Vegan, Vegetarian.
Health Effects & Notes: E621. Extensively evaluated by WHO, FDA, and EFSA; designated as safe. Mild sensitivity in rare individuals.""",

    "caffeine.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Caffeine
Category: Stimulant / Flavoring Agent
Function: Central nervous system stimulation, adds pleasant mild bitterness in cola beverages and energy drinks.
Description: Methylxanthine alkaloid naturally occurring in coffee beans, tea leaves, guarana, and cocoa beans. Also produced synthetically for soda and pre-workout formulas.
Allergen Information: Non-allergenic.
Dietary Considerations: Vegan, Vegetarian.
Health Effects & Notes: Enhances alertness. Recommended daily limit: 400 mg for adults, lower for pregnant women and children.""",

    "curcumin.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Curcumin (Turmeric Extract)
Category: Natural Food Colorant / Antioxidant
Function: Imparts bright yellow to orange-yellow color to foods like mustard, butter, cheeses, and curry powders.
Description: Bright yellow hydrophobic polyphenol extracted from the rhizomes of the turmeric plant (Curcuma longa).
Allergen Information: Non-allergenic.
Dietary Considerations: Vegan, Vegetarian.
Health Effects & Notes: E100. Strong antioxidant and anti-inflammatory natural phytonutrient.""",

    "tartrazine.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Tartrazine (FD&C Yellow No. 5)
Category: Synthetic Colorant
Function: Provides lemon-yellow color to drinks, candies, processed chips, and sauces.
Description: Synthetic azo dye soluble in water. Used widely in food, pharmaceuticals, and cosmetics.
Allergen Information: Can induce pseudo-allergic hives or respiratory reactions in aspirin-sensitive individuals.
Dietary Considerations: Vegan, Vegetarian.
Health Effects & Notes: E102. Mandatory warning label in EU regarding potential impact on activity and attention in children.""",

    "carmine.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Carmine (Cochineal Extract / E120)
Category: Natural Red Colorant
Function: Imparts deep red to pink color in yogurts, ice creams, fruit juices, and candies.
Description: Red pigment derived from crushed female cochineal insects (Dactylopius coccus) harvested from cacti.
Allergen Information: Known allergen; rare severe anaphylaxis reported due to insect protein traces.
Dietary Considerations: NOT VEGAN / NOT VEGETARIAN / NOT KOSHER / NOT HALAL.
Health Effects & Notes: E120. Must be explicitly labeled by name to inform allergic, vegan, and religious consumers.""",

    "titanium_dioxide.txt": """[INGREDIENT KNOWLEDGE BASE]
Ingredient Name: Titanium Dioxide
Category: Opacifier / White Pigment
Function: Provides bright opacity, whiteness, and shine to confectioneries, cake frostings, and gums.
Description: Naturally occurring oxide of titanium (TiO2). Insoluble mineral powder with extremely high refractive index.
Allergen Information: Non-allergenic.
Dietary Considerations: Vegan, Vegetarian.
Health Effects & Notes: E171. Banned as a food additive in the European Union (EU) due to genotoxicity concerns regarding nanoparticle accumulation."""
}

count = 0
for filename, text in documents.items():
    filepath = os.path.join(CORPUS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text.strip())
    count += 1

print(f"[SUCCESS] Generated {count} food corpus files in {CORPUS_DIR}")
