-- ============================================================
-- Script PL/SQL para APAGAR TODAS as TABELAS do usuário atual
-- Oracle Database 21.3.0.0.0
-- ATENÇÃO: Este script é DESTRUTIVO e IRREVERSÍVEL!
-- ============================================================

SET SERVEROUTPUT ON;

DECLARE
    v_sql VARCHAR2(1000);
BEGIN
    -- Loop através de todas as tabelas do usuário atual
    FOR r IN (
        SELECT table_name
        FROM user_tables
        WHERE table_name NOT LIKE 'BIN$%'  -- Exclui tabelas da lixeira (RECYCLEBIN)
        ORDER BY table_name
    ) LOOP
        -- Monta e executa o comando DROP TABLE com CASCADE CONSTRAINTS
        v_sql := 'DROP TABLE ' || r.table_name || ' CASCADE CONSTRAINTS PURGE';
        
        BEGIN
            EXECUTE IMMEDIATE v_sql;
            DBMS_OUTPUT.PUT_LINE('Tabela apagada: ' || r.table_name);
        EXCEPTION
            WHEN OTHERS THEN
                DBMS_OUTPUT.PUT_LINE('Erro ao apagar ' || r.table_name || ': ' || SQLERRM);
        END;
    END LOOP;
    
    DBMS_OUTPUT.PUT_LINE('Processo concluído. Todas as tabelas foram removidas.');
END;
/
exit ; 
/
