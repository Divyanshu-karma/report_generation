# TAE Golden Regression Suite Run - RUN-20260721-141531
* **Run Mode**: strict
* **Regression Suite Version**: 2.2.0
* **Completed At**: 2026-07-21T14:15:31.462214+00:00
* **CI Status**: **FAIL**

## Summary
| Metric | Value | Denominator/Context |
|---|---|---|
| Total Cases (total rows) | 241 | Total cases in golden suite |
| Active Gating Cases (active gating rows) | 171 | Active cases that block release |
| Advisory Cases (advisory rows) | 70 | Advisory cases (informational) |
| Passed | 215 | Successful case runs (excluding release-blocking failures) |
| Pass-with-Warning Cases (pass-with-warning rows) | 27 | Passed with calibration warnings |
| Release-Blocking Failures | 17 | Active gating cases that failed |
| Advisory Failures | 9 | Advisory cases that failed (informational) |
| Total Failures | 26 | All failures (release-blocking + advisory) |
|   - Risk Mismatch Failures | 16 | Unique rows with incorrect risk assessments |
|   - Risk Mismatch Category Hits | 30 | Raw per-category failure count (rows × categories) |
|   - Confidence-Only Failures | 10 | Failures caused strictly by confidence mismatch/plumbing |
|   - Trace/Metadata Failures | 0 | Failures due to trace integrity issues |
|   - Doctrine/Guardrail Failures | 1 | Failures due to incorrect/missing doctrine or guardrail triggers |
|   - Citation Resolution Failures | 0 | Failures resolving cited trademark identifiers |
|   - LLM Validation Failures | 0 | Failures caused by disabled or mismatched LLM validation |
|   - Confidence Out of Range Rows | 10 | Total failed rows with any confidence failure |
|   - True Confidence-Only Failures | 9 | Failures caused strictly by confidence |
|   - Risk and Confidence Combined Failures | 1 | Failures with both risk and confidence issues |
|   - Risk-Only Failures | 15 | Substantive risk mismatches without confidence issues |
|   - Rows Blocked Due to Incomplete Fixture | 0 | Fixtures not evaluated for confidence due to missing/placeholder evidence |
|   - Rows Evaluated with Complete Evidence | 241 | Fixtures evaluated with complete evidence |
| Tier 2 Warnings | 27 | Total calibration warnings across run |
|   - Missing Confidence Count | 0 | Total rows missing confidence field/value |
|   - Invalid Confidence Count | 0 | Total rows with non-numeric or out of bounds confidence |
|   - Out of Range Confidence Count | 10 | Total rows where confidence is outside expected range |

## LLM Validation Summary
| Metric | Value | Description |
|---|---|---|
| Validation Mode | validation_live | Execution mode for LLM validation |
| LLM Eligible Count | 105 | Citations meeting eligibility thresholds |
| LLM Submitted Count | 105 | Citations submitted/attempted |
| LLM Completed Count | 105 | Successful validation runs |
|   - Completed from Live API | 105 | Completed from live LLM requests |
|   - Completed from Cache | 0 | Completed from local cache |
|   - Completed from Synthetic Fallback | 0 | Completed from synthetic/fallback data |
| LLM Skipped Count | 337 | Skipped validation attempts |
| LLM Failed Count | 0 | Failed validation attempts |
| LLM Unavailable Count | 0 | Skipped due to service/cache unavailable |
| LLM Skipped Ineligible Count | 337 | Skipped due to generic description |
| LLM Skipped Due to Cap | 0 | Skipped due to batch cap limit |

## Case Results
| Case | Sub-Case | Gating Tier | Status | Expected Risk | Actual Risk | Failures | Warnings |
|---|---|---|---|---|---|---|---|
| bonbonfruit | ab_amsterdamsche_bonbons_xxx_and_design | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| bonbonfruit | bonbon_cafe | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| bonbonfruit | bonbon_matcha_and_design | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| bonbonfruit | bon_bon | advisory | **PASS** | MEDIUM_LOW | MEDIUM | None | None |
| bonbonfruit | bon_bon_bum_power | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM | None | None |
| bonbonfruit | classic_bon_bons | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| creamsicle | cransicle | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| creamsicle | cream | advisory | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_HIGH | MEDIUM | None | Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' |
| creamsicle | creamstillery | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| creamsicle | cream_city | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| creamsicle | cream_creamsicle | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| creamsicle | cream_heroes_and_design | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| creamsicle | cream_of_kentucky | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_LOW | LOW | None | Confidence 0.500 outside expected range [0.600, 0.950] |
| creamsicle | cream_puff | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| creamsicle | cream_sugar_please | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| creamsicle | grapesicle | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| creamsicle | icesicle | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_LOW | LOW | None | Confidence 0.500 outside expected range [0.600, 0.950] |
| creamsicle | it_was_all_a_dream_sicle | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| creamsicle | m_43_orange_creamsicle | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_HIGH | MEDIUM | None | Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' |
| creamsicle | m_43_pi_a_colada_creamsicle | advisory | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_HIGH | MEDIUM | None | Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' |
| creamsicle | m_43_raspberry_creamsicle | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_HIGH | MEDIUM | None | Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' |
| creamsicle | orange_dreamsicle | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| creamsicle | orange_shinesicle | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| creamsicle | pina_colada_creamsicle | advisory | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_HIGH | MEDIUM | None | Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' |
| creamsicle | powersicle | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| creamsicle | puffsicle | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_LOW | LOW | None | Confidence 0.500 outside expected range [0.600, 0.950] |
| creamsicle | rumsicles | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| creamsicle | whipsicle | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_LOW | LOW | None | Confidence 0.500 outside expected range [0.600, 0.950] |
| crispycoatingsmix | columbus_mix | release_blocking | **PASS** | LOW | LOW | None | None |
| crispycoatingsmix | couch_mix | release_blocking | **PASS** | LOW | LOW | None | None |
| crispycoatingsmix | country_mix | release_blocking | **FAIL — CONFIDENCE_ONLY** | LOW | LOW | Confidence 0.500 outside expected range [0.600, 0.950] | None |
| crispycoatingsmix | crispycoat | advisory | **FAIL** | HIGH | MEDIUM_LOW | Risk level 'MEDIUM_LOW' not in allowed range ['MEDIUM_HIGH', 'HIGH'] and not an acceptable transition from 'HIGH', Risk level 'MEDIUM_LOW' fell below required escalation workflow threshold 'MEDIUM_HIGH' | None |
| crispycoatingsmix | crispycubes | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| crispycoatingsmix | crispy_beef_jerky | release_blocking | **FAIL — CONFIDENCE_ONLY** | LOW | LOW | Confidence 0.295 outside expected range [0.600, 0.950] | None |
| crispycoatingsmix | crispy_calamari | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| crispycoatingsmix | crispy_chicken_chips | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| crispycoatingsmix | crispy_clouds | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| crispycoatingsmix | crispy_clouds_and_design | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| crispycoatingsmix | crispy_coatings | release_blocking | **FAIL** | HIGH | MEDIUM_LOW | Risk level 'MEDIUM_LOW' not in allowed range ['MEDIUM_HIGH', 'HIGH'] and not an acceptable transition from 'HIGH', Risk level 'MEDIUM_LOW' fell below required escalation workflow threshold 'MEDIUM_HIGH' | None |
| crispycoatingsmix | crispy_cravers | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| crispycoatingsmix | crispy_crowns | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| crispycoatingsmix | crispy_crunchies | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| crispycoatingsmix | crispy_curls | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| crispycoatingsmix | crispy_cuts | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| crispycoatingsmix | crispy_king | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| crispycoatingsmix | crispy_kitchen | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| crispycoatingsmix | ensley_seasoned_coating_mix | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| cypressrush | cipres_mint | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| cypressrush | cr_cypress_ridge_body_and_design_or_cypress_ridge_body | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| cypressrush | cypress_fir | advisory | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| cypressrush | cypress_moon_soap_company | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| cypressrush | cypress_musings | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| cypressrush | cypres_pantelleria_armani_prive | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| depth_signal | cell_signal_serum | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM | None | None |
| depth_signal | c_signaling_cosmetics | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| depth_signal | depth_design | advisory | **PASS** | MEDIUM_LOW | MEDIUM | None | None |
| depth_signal | ds_dr_signal_and_design_ds_dr_signal | advisory | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| depth_signal | signalsource_technology | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM | None | None |
| depth_signal | skin_signal | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM | None | None |
| depth_signal | surface_depth | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM | None | None |
| dualfusion_complex | Monolithic | release_blocking | **FAIL** | MEDIUM_LOW | MEDIUM_HIGH | Risk level 'MEDIUM_HIGH' not in allowed range ['MEDIUM_LOW', 'MEDIUM'] and not an acceptable transition from 'MEDIUM_LOW' | None |
| dualfusioncomplex | amino_fusion | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | antifade_complex | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | arthrofusion | release_blocking | **FAIL — CONFIDENCE_ONLY** | LOW | LOW | Confidence 0.500 outside expected range [0.600, 0.950] | None |
| dualfusioncomplex | bariatric_fusion | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | biotin_fusion_complex | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | calmcact_complex | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | cer_amino_complex | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | color_fusion | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | colourfix3_complex | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | curl_fusion | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | dual | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | dualpolar | release_blocking | **FAIL — CONFIDENCE_ONLY** | LOW | LOW | Confidence 0.500 outside expected range [0.600, 0.950] | None |
| dualfusioncomplex | dualsenses | release_blocking | **FAIL — CONFIDENCE_ONLY** | LOW | LOW | Confidence 0.500 outside expected range [0.600, 0.950] | None |
| dualfusioncomplex | dual_action_acidophilus_bifidus | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | dual_action_cla_cut | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | dual_action_cleanse | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | dual_action_fat_burner_red | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | dual_biactive_d_tox | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | dual_channel_hydration | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | dual_defense_prostate_support | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | dual_face | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | dual_health_body_and_mind | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | dual_impact | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | dual_mag_complex | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | dual_prenatal_immunity | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | dual_therapy | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | dual_tox_dpo | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | dual_weight_protein_complex | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | d_aminolift_complex | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | frizzlock_complex | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | fusion | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | fusion_and_design | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | hair_fusion | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | hair_fusion_and_design | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | hydrafusion | release_blocking | **PASS** | LOW | MEDIUM | None | None |
| dualfusioncomplex | kerabiotin_fusion | release_blocking | **PASS** | LOW | LOW | None | None |
| dualfusioncomplex | keratin_complex | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | klean_complex | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | moisturfusion | release_blocking | **FAIL — CONFIDENCE_ONLY** | LOW | LOW | Confidence 0.500 outside expected range [0.600, 0.950] | None |
| dualfusioncomplex | nutra3_complex_and_design | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | nutractive_complex | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | nutra_complex | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | nutri_cell_complex | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| dualfusioncomplex | vitafusion | release_blocking | **FAIL — CONFIDENCE_ONLY** | LOW | LOW | Confidence 0.500 outside expected range [0.600, 0.950] | None |
| eclipse | body_eclipse | release_blocking | **PASS** | LOW | LOW | None | None |
| eclipse | body_eclipse_club | release_blocking | **PASS** | LOW | LOW | None | None |
| eclipse | body_eclipse_natural | release_blocking | **PASS** | LOW | LOW | None | None |
| eclipse | cutter_eclipse | advisory | **PASS** | LOW | LOW | None | None |
| eclipse | daily_eclipse | release_blocking | **PASS** | LOW | LOW | None | None |
| eclipse | eclipse | release_blocking | **PASS** | HIGH | HIGH | None | None |
| eclipse | eclipse_cure | advisory | **PASS** | LOW | LOW | None | None |
| eclipse | eclipse_exact | advisory | **PASS** | HIGH | HIGH | None | None |
| eclipse | eclipse_hemp | advisory | **PASS** | LOW | LOW | None | None |
| eclipse | eclipse_instant_hair_filler | advisory | **PASS** | LOW | LOW | None | None |
| eclipse | eclipse_microglide | release_blocking | **PASS** | LOW | LOW | None | None |
| eclipse | eclipse_spa_body | release_blocking | **PASS** | LOW | LOW | None | None |
| eclipse | eglips | advisory | **FAIL** | HIGH | MEDIUM | Risk level 'MEDIUM' not in allowed range ['MEDIUM_HIGH', 'HIGH'] and not an acceptable transition from 'HIGH', Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' | None |
| eclipse | eternal_eclipse | advisory | **PASS** | LOW | LOW | None | None |
| eclipse | ghost_eclipse | advisory | **PASS** | LOW | LOW | None | None |
| eclipse | hyprskn_eclipse | advisory | **PASS** | LOW | LOW | None | None |
| eclipse | mystic_kiss_eclipse_night_cream | advisory | **PASS** | LOW | LOW | None | None |
| eclipse | shaquille_o_neal_eqlipse | advisory | **PASS** | LOW | MEDIUM | None | None |
| exact_identity_crowded_field_collision | Monolithic | release_blocking | **FAIL** | MEDIUM_HIGH | HIGH | Required guardrail 'crowded_field_guardrail' was not triggered | None |
| feeltheflavor | feeling_saucy | release_blocking | **PASS** | LOW | LOW | None | None |
| feeltheflavor | feelin_saucy | release_blocking | **PASS** | LOW | LOW | None | None |
| feeltheflavor | feel_the_difference | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| feeltheflavor | feel_the_effect | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| feeltheflavor | feel_the_flavor | release_blocking | **PASS (Can be improved)** | MEDIUM_HIGH | HIGH | None | None |
| feeltheflavor | feel_the_flavor_taste_the_heat | release_blocking | **PASS** | LOW | LOW | None | None |
| feeltheflavor | feel_the_heat_share_the_joy | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| feeltheflavor | feel_the_lift | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| feeltheflavor | feel_the_love | release_blocking | **PASS** | LOW | LOW | None | None |
| feeltheflavor | feel_the_moment | release_blocking | **PASS** | LOW | LOW | None | None |
| feeltheflavor | feel_the_sun | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| feeltheflavor | flavors_you_feel | release_blocking | **PASS** | LOW | LOW | None | None |
| feeltheflavor | krunch_the_flavor | release_blocking | **PASS** | LOW | LOW | None | None |
| feeltheflavor | savor_the_flavor | release_blocking | **PASS** | LOW | LOW | None | None |
| feeltheflavor | the_flavor_you_can_feel | release_blocking | **PASS** | LOW | LOW | None | None |
| feeltheflavor | untwist_the_flavor | release_blocking | **PASS** | LOW | LOW | None | None |
| feeltheflavor | we_bring_the_flavor | release_blocking | **PASS** | LOW | LOW | None | None |
| firecracker | firecracker | release_blocking | **PASS** | HIGH | HIGH | None | None |
| firecracker | firework | release_blocking | **FAIL** | HIGH | MEDIUM | Risk level 'MEDIUM' not in allowed range ['MEDIUM_HIGH', 'HIGH'] and not an acceptable transition from 'HIGH', Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' | None |
| fresh_clubhouse | farmhouse_fresh | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | fhf_farmhouse_fresh | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | fresh | advisory | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | freshcare | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | freshcult | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | freshcycle | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | fresherbs | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | freshface | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | freshlocs | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | fresh_breath | advisory | **PASS** | LOW | LOW | None | None |
| fresh_clubhouse | fresh_chemistry | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | fresh_choice | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | fresh_cotton | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | fresh_cream | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | fresh_kidz | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | fresh_mouth | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | honey_house_fresh | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| fresh_clubhouse | pnk_clubhouse_cosmetics | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| iykygifyouknowyouglow | iykyk | advisory | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_HIGH | MEDIUM | None | Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' |
| iykygifyouknowyouglow | makari | advisory | **FAIL — RISK_AND_CONFIDENCE** | MEDIUM_HIGH | LOW | Risk level 'LOW' not in allowed range ['MEDIUM', 'MEDIUM_HIGH'] and not an acceptable transition from 'MEDIUM_HIGH', Risk level 'LOW' fell below required escalation workflow threshold 'MEDIUM_HIGH', Confidence 0.500 outside expected range [0.600, 0.950] | None |
| iykygifyouknowyouglow | makari_iykyk | advisory | **FAIL** | HIGH | MEDIUM | Risk level 'MEDIUM' not in allowed range ['MEDIUM_HIGH', 'HIGH'] and not an acceptable transition from 'HIGH', Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' | None |
| iykygifyouknowyouglow | the_more_you_go_the_more_you_glow | release_blocking | **PASS** | LOW | MEDIUM | None | None |
| iykygifyouknowyouglow | uglowbeauty | release_blocking | **FAIL — CONFIDENCE_ONLY** | LOW | LOW | Confidence 0.500 outside expected range [0.600, 0.950] | None |
| iykygifyouknowyouglow | you_glow_girl | release_blocking | **PASS** | LOW | MEDIUM | None | None |
| iykygifyouknowyouglow | yo_glow | release_blocking | **PASS** | LOW | LOW | None | None |
| iykygifyouknowyouglow | yuglo | release_blocking | **FAIL — CONFIDENCE_ONLY** | LOW | LOW | Confidence 0.500 outside expected range [0.600, 0.950] | None |
| magnum | Monolithic | release_blocking | **PASS (Can be improved)** | HIGH | MEDIUM_HIGH | None | None |
| peacepoppers | hopper_s_poppers | advisory | **PASS** | LOW | MEDIUM_LOW | None | None |
| peacepoppers | peace_by_chocolate | release_blocking | **PASS** | LOW | LOW | None | None |
| peacepoppers | peace_chew | release_blocking | **PASS** | LOW | LOW | None | None |
| peacepoppers | peace_love_and_chocolate | release_blocking | **PASS** | MEDIUM | LOW | None | None |
| peacepoppers | peace_pie | release_blocking | **FAIL** | HIGH | MEDIUM_LOW | Risk level 'MEDIUM_LOW' not in allowed range ['MEDIUM_HIGH', 'HIGH'] and not an acceptable transition from 'HIGH', Risk level 'MEDIUM_LOW' fell below required escalation workflow threshold 'MEDIUM_HIGH' | None |
| peacepoppers | peace_pops | release_blocking | **FAIL** | HIGH | MEDIUM_LOW | Risk level 'MEDIUM_LOW' not in allowed range ['MEDIUM_HIGH', 'HIGH'] and not an acceptable transition from 'HIGH', Risk level 'MEDIUM_LOW' fell below required escalation workflow threshold 'MEDIUM_HIGH' | None |
| peacepoppers | protein_poppers | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| pieceofpeace | from_pieces_to_peace | advisory | **PASS** | MEDIUM_LOW | MEDIUM | None | None |
| pieceofpeace | peace_by_pieceby_face | advisory | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| pieceofpeace | peace_chew | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| pieceofpeace | peace_pie | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| pieceofpeace | peace_pops | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| pieceofpeace | peace_x_piece_and_design_peacex_piece | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| pieceofpeace | pieces | advisory | **PASS** | MEDIUM_LOW | MEDIUM | None | None |
| pieceofpeace | pieces_for_peace | advisory | **PASS** | MEDIUM_LOW | MEDIUM | None | None |
| pieceofpeace | pieces_of_peace | advisory | **PASS** | MEDIUM_LOW | MEDIUM | None | None |
| pieceofpeace | piece_of_cake | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| pieceofpeace | piece_of_peace | advisory | **FAIL** | MEDIUM_LOW | HIGH | Risk level 'HIGH' not in allowed range ['LOW', 'MEDIUM_LOW'] and not an acceptable transition from 'MEDIUM_LOW', Risk level 'HIGH' incorrectly escalated above workflow threshold 'MEDIUM_HIGH' | None |
| pieceofpeace | sugar_peace | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| poppables | oh_so_poppable | advisory | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_HIGH | MEDIUM | None | Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' |
| poppables | peace_pie | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_LOW | LOW | None | Confidence 0.500 outside expected range [0.600, 0.900] |
| poppables | poppables | advisory | **PASS (Can be improved)** | MEDIUM_HIGH | HIGH | None | None |
| poppables | pop_a_pples_and_design_pop_a_pples | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| poppables | protein_poppables | release_blocking | **FAIL** | HIGH | MEDIUM | Risk level 'MEDIUM' not in allowed range ['MEDIUM_HIGH', 'HIGH'] and not an acceptable transition from 'HIGH', Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' | None |
| poppables | sodapops_poppable_sparkling_soda_flavored_chocolate_bites_and_design | advisory | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| poppables | taste_the_poppabilities | advisory | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_HIGH | MEDIUM | None | Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' |
| poppables | tropical_poppables | release_blocking | **FAIL** | HIGH | MEDIUM | Risk level 'MEDIUM' not in allowed range ['MEDIUM_HIGH', 'HIGH'] and not an acceptable transition from 'HIGH', Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' | None |
| poppables | untwist_the_flavor | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_LOW | LOW | None | Confidence 0.295 outside expected range [0.600, 0.900] |
| razzup | blue_razz | advisory | **PASS** | LOW | MEDIUM | None | None |
| razzup | razz | release_blocking | **PASS** | LOW | MEDIUM | None | None |
| razzup | razzapple_magic_dip | release_blocking | **PASS** | LOW | MEDIUM | None | None |
| razzup | rise_up | release_blocking | **PASS** | LOW | MEDIUM_LOW | None | None |
| razzup | rise_up_and_design | release_blocking | **PASS** | LOW | MEDIUM | None | None |
| score_normalization_restoration_control | Monolithic | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| synbiosis | pro_symbiotics | advisory | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_HIGH | MEDIUM | None | Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' |
| synbiosis | symbeeosis | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_HIGH | MEDIUM | None | Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' |
| synbiosis | symbeeosis_and_design_symbeeosis | advisory | **FAIL** | MEDIUM_HIGH | MEDIUM_LOW | Risk level 'MEDIUM_LOW' not in allowed range ['MEDIUM', 'MEDIUM_HIGH'] and not an acceptable transition from 'MEDIUM_HIGH', Risk level 'MEDIUM_LOW' fell below required escalation workflow threshold 'MEDIUM_HIGH' | None |
| synbiosis | symbiosis | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_HIGH | MEDIUM | None | Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' |
| synbiosis | symbiosis_londonsymbiosis_london | advisory | **FAIL** | MEDIUM_HIGH | LOW | Risk level 'LOW' not in allowed range ['MEDIUM', 'MEDIUM_HIGH'] and not an acceptable transition from 'MEDIUM_HIGH', Risk level 'LOW' fell below required escalation workflow threshold 'MEDIUM_HIGH' | None |
| synbiosis | symbiotic | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_HIGH | MEDIUM | None | Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' |
| synbiosis | symbiotics | advisory | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_HIGH | MEDIUM | None | Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' |
| synbiosis | symbiotic_and_design_sym_biotic | advisory | **FAIL** | MEDIUM_HIGH | LOW | Risk level 'LOW' not in allowed range ['MEDIUM', 'MEDIUM_HIGH'] and not an acceptable transition from 'MEDIUM_HIGH', Risk level 'LOW' fell below required escalation workflow threshold 'MEDIUM_HIGH' | None |
| synbiosis | synbiotic | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_HIGH | MEDIUM | None | Risk level 'MEDIUM' fell below required escalation workflow threshold 'MEDIUM_HIGH' |
| themagnumicecreamcompany | cougar_magnum | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| themagnumicecreamcompany | magnima_and_design | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| themagnumicecreamcompany | magnum | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM | None | None |
| themagnumicecreamcompany | magnum_44 | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_LOW | LOW | None | Confidence 0.500 outside expected range [0.600, 0.950] |
| themagnumicecreamcompany | magnum_band | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| themagnumicecreamcompany | magnum_club | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| themagnumicecreamcompany | magnum_dental | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| themagnumicecreamcompany | magnum_funds | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| themagnumicecreamcompany | magnum_insurance | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| themagnumicecreamcompany | magnum_insurance_agency | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| themagnumicecreamcompany | magnum_mondays | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_LOW | LOW | None | Confidence 0.500 outside expected range [0.600, 0.950] |
| themagnumicecreamcompany | magnum_photos | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| themagnumicecreamcompany | magnum_pure | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_LOW | LOW | None | Confidence 0.295 outside expected range [0.600, 0.950] |
| themagnumicecreamcompany | magnum_p_i | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_LOW | LOW | None | Confidence 0.500 outside expected range [0.600, 0.950] |
| themagnumicecreamcompany | magnum_research | release_blocking | **PASS** | MEDIUM_LOW | MEDIUM | None | None |
| themagnumicecreamcompany | magnum_seguros | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| themagnumicecreamcompany | magnum_trailers | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| themagnumicecreamcompany | mvp_magnum_venus_products_and_design | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_LOW | LOW | None | Confidence 0.500 outside expected range [0.600, 0.950] |
| themagnumicecreamcompany | m_magnum_cellars_and_design | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_LOW | LOW | None | Confidence 0.500 outside expected range [0.600, 0.950] |
| themagnumicecreamcompany | seguros_magnum | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| themagnumicecreamcompany | signum_magnum_university_and_design | release_blocking | **PASS_WITH_CALIBRATION_WARNINGS** | MEDIUM_LOW | LOW | None | Confidence 0.500 outside expected range [0.600, 0.950] |
| themagnumicecreamcompany | the_magnum_opus | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| themagnumicecreamcompany | true_magnum | release_blocking | **PASS** | MEDIUM_LOW | LOW | None | None |
| ward | cedar_ward | release_blocking | **PASS** | MEDIUM | MEDIUM | None | None |
| ward | wardash | advisory | **FAIL** | MEDIUM_LOW | MEDIUM_HIGH | Risk level 'MEDIUM_HIGH' not in allowed range ['LOW', 'MEDIUM_LOW'] and not an acceptable transition from 'MEDIUM_LOW' | None |
| ward | warden | release_blocking | **PASS** | MEDIUM_HIGH | MEDIUM_HIGH | None | None |
| ward | wardley | advisory | **PASS** | MEDIUM_LOW | MEDIUM_LOW | None | None |
| ward | ward_smelling_salts | advisory | **PASS** | MEDIUM_LOW | MEDIUM | None | None |

## Governance Summary
| Metric | Value |
|---|---|
| Golden Suite Version | 2.2.0 |
| Calibration Version | 2026.07.08.1 |
| Fixture Tree SHA256 | 126c6c9cf7c91a99fa750713c8c81f2af0fa3c8f807019d771d0e5f93cdbb301 |
| Change Record ID | GT-2026-07-08-001 |
| Fixture Hash Verified | True |
| Schema Validated | True |
| Placeholder Goods Count | 49 |
| Attorney-Confirmed Active Count | 171 |
| Advisory Count | 70 |