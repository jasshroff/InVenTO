
CREATE SCHEMA IF NOT EXISTS `jewellery_inventory` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `jewellery_inventory` ;

-- -----------------------------------------------------
-- Table `jewellery_inventory`.`category`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `jewellery_inventory`.`category` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name` (`name` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 5
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `jewellery_inventory`.`customer`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `jewellery_inventory`.`customer` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(120) NULL DEFAULT NULL,
  `phone` VARCHAR(20) NULL DEFAULT NULL,
  `address` TEXT NULL DEFAULT NULL,
  `birthdate` DATE NULL DEFAULT NULL,
  `anniversary` DATE NULL DEFAULT NULL,
  `preferences` TEXT NULL DEFAULT NULL,
  `ring_size` VARCHAR(10) NULL DEFAULT NULL,
  `bracelet_size` VARCHAR(10) NULL DEFAULT NULL,
  `necklace_length` VARCHAR(10) NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `jewellery_inventory`.`customers`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `jewellery_inventory`.`customers` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `contact` VARCHAR(20) NOT NULL,
  `address` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `contact` (`contact` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `jewellery_inventory`.`inventory`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `jewellery_inventory`.`inventory` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `category` VARCHAR(255) NOT NULL,
  `price` FLOAT NOT NULL,
  `quantity` INT NOT NULL,
  `barcode` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `barcode` (`barcode` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `jewellery_inventory`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `jewellery_inventory`.`user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(64) NOT NULL,
  `email` VARCHAR(120) NOT NULL,
  `password_hash` VARCHAR(256) NOT NULL,
  `is_admin` TINYINT(1) NULL DEFAULT NULL,
  `date_joined` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username` (`username` ASC) VISIBLE,
  UNIQUE INDEX `email` (`email` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `jewellery_inventory`.`invoice`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `jewellery_inventory`.`invoice` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `invoice_number` VARCHAR(50) NOT NULL,
  `customer_id` INT NOT NULL,
  `issue_date` DATETIME NULL DEFAULT NULL,
  `due_date` DATETIME NULL DEFAULT NULL,
  `total_amount` DECIMAL(10,2) NULL DEFAULT NULL,
  `tax_amount` DECIMAL(10,2) NULL DEFAULT NULL,
  `discount` DECIMAL(10,2) NULL DEFAULT NULL,
  `final_amount` DECIMAL(10,2) NULL DEFAULT NULL,
  `is_custom_order` TINYINT(1) NULL DEFAULT NULL,
  `is_repair` TINYINT(1) NULL DEFAULT NULL,
  `estimated_ready_date` DATETIME NULL DEFAULT NULL,
  `deposit_amount` DECIMAL(10,2) NULL DEFAULT NULL,
  `warranty_period` INT NULL DEFAULT NULL,
  `appraisal_value` DECIMAL(10,2) NULL DEFAULT NULL,
  `status` VARCHAR(20) NULL DEFAULT NULL,
  `payment_method` VARCHAR(50) NULL DEFAULT NULL,
  `notes` TEXT NULL DEFAULT NULL,
  `created_by` INT NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `invoice_number` (`invoice_number` ASC) VISIBLE,
  INDEX `customer_id` (`customer_id` ASC) VISIBLE,
  INDEX `created_by` (`created_by` ASC) VISIBLE,
  CONSTRAINT `invoice_ibfk_1`
    FOREIGN KEY (`customer_id`)
    REFERENCES `jewellery_inventory`.`customer` (`id`),
  CONSTRAINT `invoice_ibfk_2`
    FOREIGN KEY (`created_by`)
    REFERENCES `jewellery_inventory`.`user` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 15
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `jewellery_inventory`.`supplier`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `jewellery_inventory`.`supplier` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `contact_person` VARCHAR(100) NULL DEFAULT NULL,
  `email` VARCHAR(120) NULL DEFAULT NULL,
  `phone` VARCHAR(20) NULL DEFAULT NULL,
  `address` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `jewellery_inventory`.`product`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `jewellery_inventory`.`product` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT NULL DEFAULT NULL,
  `barcode` VARCHAR(5) NULL DEFAULT NULL,
  `price` DECIMAL(10,2) NOT NULL,
  `cost_price` DECIMAL(10,2) NULL DEFAULT NULL,
  `quantity` INT NULL DEFAULT NULL,
  `material` VARCHAR(50) NULL DEFAULT NULL,
  `metal_type` VARCHAR(50) NULL DEFAULT NULL,
  `purity` VARCHAR(20) NULL DEFAULT NULL,
  `stone_type` VARCHAR(50) NULL DEFAULT NULL,
  `stone_count` INT NULL DEFAULT NULL,
  `stone_carat` DECIMAL(10,2) NULL DEFAULT NULL,
  `weight` DECIMAL(10,3) NULL DEFAULT NULL,
  `size` VARCHAR(20) NULL DEFAULT NULL,
  `category_id` INT NULL DEFAULT NULL,
  `supplier_id` INT NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `sku` (`barcode` ASC) VISIBLE,
  INDEX `category_id` (`category_id` ASC) VISIBLE,
  INDEX `supplier_id` (`supplier_id` ASC) VISIBLE,
  CONSTRAINT `product_ibfk_1`
    FOREIGN KEY (`category_id`)
    REFERENCES `jewellery_inventory`.`category` (`id`),
  CONSTRAINT `product_ibfk_2`
    FOREIGN KEY (`supplier_id`)
    REFERENCES `jewellery_inventory`.`supplier` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `jewellery_inventory`.`jewelry_service`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `jewellery_inventory`.`jewelry_service` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT NULL DEFAULT NULL,
  `service_type` VARCHAR(50) NOT NULL,
  `price` DECIMAL(10,2) NOT NULL,
  `duration` INT NULL DEFAULT NULL,
  `materials_needed` TEXT NULL DEFAULT NULL,
  `difficulty_level` VARCHAR(20) NULL DEFAULT NULL,
  `requires_deposit` TINYINT(1) NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `jewellery_inventory`.`invoice_item`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `jewellery_inventory`.`invoice_item` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `invoice_id` INT NOT NULL,
  `product_id` INT NOT NULL,
  `quantity` INT NOT NULL,
  `unit_price` DECIMAL(10,2) NOT NULL,
  `total_price` DECIMAL(10,2) NOT NULL,
  `is_service` TINYINT(1) NULL DEFAULT NULL,
  `service_id` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `invoice_id` (`invoice_id` ASC) VISIBLE,
  INDEX `product_id` (`product_id` ASC) VISIBLE,
  INDEX `service_id` (`service_id` ASC) VISIBLE,
  CONSTRAINT `invoice_item_ibfk_1`
    FOREIGN KEY (`invoice_id`)
    REFERENCES `jewellery_inventory`.`invoice` (`id`),
  CONSTRAINT `invoice_item_ibfk_2`
    FOREIGN KEY (`product_id`)
    REFERENCES `jewellery_inventory`.`product` (`id`),
  CONSTRAINT `invoice_item_ibfk_3`
    FOREIGN KEY (`service_id`)
    REFERENCES `jewellery_inventory`.`jewelry_service` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 17
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `jewellery_inventory`.`sales`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `jewellery_inventory`.`sales` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `item_id` INT NOT NULL,
  `customer_name` VARCHAR(255) NOT NULL,
  `customer_contact` VARCHAR(20) NOT NULL,
  `total_price` FLOAT NOT NULL,
  `date` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `item_id` (`item_id` ASC) VISIBLE,
  CONSTRAINT `sales_ibfk_1`
    FOREIGN KEY (`item_id`)
    REFERENCES `jewellery_inventory`.`inventory` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `jewellery_inventory`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `jewellery_inventory`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username` (`username` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
