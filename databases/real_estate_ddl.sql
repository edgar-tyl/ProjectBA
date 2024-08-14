CREATE TABLE ApartmentDetails (
            ApartmentAddress TEXT,
            ApartmentID INTEGER PRIMARY KEY,
            Size INTEGER,
            NumberOfRooms INTEGER,
            NumberOfBathrooms INTEGER,
            Balcony BOOLEAN
        );
CREATE TABLE ApartmentDescription (
            ApartmentID INTEGER,
            Description TEXT,
            FOREIGN KEY (ApartmentID) REFERENCES ApartmentDetails (ApartmentID)
        );
CREATE TABLE ApartmentRatings (
            ApartmentID INTEGER,
            Rating INTEGER,
            Text TEXT,
            FOREIGN KEY (ApartmentID) REFERENCES ApartmentDetails (ApartmentID)
        );
CREATE TABLE ApartmentOwnership (
            ApartmentID INTEGER,
            OwnerID INTEGER,
            TransferID INTEGER,
            FOREIGN KEY (ApartmentID) REFERENCES ApartmentDetails (ApartmentID),
            FOREIGN KEY (OwnerID) REFERENCES Owners (OwnerID),
            FOREIGN KEY (TransferID) REFERENCES OwnershipTransfers (TransferID)
        );
CREATE TABLE OwnershipTransfers (
            TransferID INTEGER PRIMARY KEY,
            Price REAL,
            Date TEXT
        );
CREATE TABLE Owners (
            OwnerID INTEGER PRIMARY KEY,
            OwnerName TEXT,
            Address TEXT
        );
