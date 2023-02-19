CREATE TABLE enriched_billing_codes AS
SELECT
    billing_code,
    drg_mdc.mdc as drg_mdc,
    drg_mdc.type as drg_mdc_type,
    drg_mdc.mdc_description as mdc_description,
    apr_drg.mdc as apr_mdc,
    apr_drg.type as apr_type
FROM (
    SELECT DISTINCT billing_code, negotiation_arrangement
    FROM innetwork
    WHERE
        negotiation_arrangement = 'ffs'
) as in_network_codes
LEFT JOIN (
    SELECT
        drg,
        mdc,
        "type",
        "long description" as mdc_description
    FROM drg_mdc
) as drg_mdc
ON in_network_codes.billing_code = drg_mdc.drg
LEFT JOIN (
    SELECT drg, mdc, "type"
    FROM apr_drg
) as apr_drg
ON in_network_codes.billing_code = apr_drg.drg