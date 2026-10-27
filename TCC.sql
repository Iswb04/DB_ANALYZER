CREATE USER 'app'@'localhost' IDENTIFIED BY '1234';
GRANT ALL PRIVILEGES ON store.* TO 'app'@'localhost';
FLUSH PRIVILEGES;

SELECT * FROM produtos;

SET SQL_SAFE_UPDATES = 0;
DELETE FROM produtos;  # deletar produtos
TRUNCATE TABLE produtos; # deletar produtos e reiniciar IDs
SET SQL_SAFE_UPDATES = 1;


DELETE FROM nome_da_tabela
WHERE id = 21;

SELECT * FROM produtos;
SELECT COUNT(*) FROM produtos;




TRUNCATE TABLE vendas;
DROP TABLE vendas;