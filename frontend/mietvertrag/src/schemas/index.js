import wgSchema from "./wg.schema.js";
import apartmentSchema from "./apartment.schema.js";
import houseSchema from "./house.schema.js";
import garageSchema from "./garage.schema.js";
import storageSchema from "./storage.schema.js";
import commercialSchema from "./commercial.schema.js";
import zwischenmieteSchema from "./zwischenmiete.schema.js";
import untervermietungSchema from "./untervermietung.schema.js";

const SCHEMA_MAP = {
  wg: wgSchema,
  apartment: apartmentSchema,
  house: houseSchema,
  garage: garageSchema,
  storage: storageSchema,
  commercial: commercialSchema,
  zwischenmiete: zwischenmieteSchema,
  untervermietung: untervermietungSchema,
};

export function loadSchema(schemaId) {
  return SCHEMA_MAP[schemaId] || null;
}

export default SCHEMA_MAP;
