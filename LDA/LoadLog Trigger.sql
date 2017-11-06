CREATE TRIGGER LDA_updateLog
AFTER UPDATE ON LDA_Transformer
FOR EACH ROW
BEGIN
INSERT INTO LDA_LoadLog (Load, Time, Transformer_ID) values (new.load, strftime('%Y-%m-%d %H:%M:%f'), new.id);
END ;