#!/usr/bin/env bash
set -euo pipefail

docker exec mongo mongosh -u admin -p root --authenticationDatabase admin sentimentstream --eval '
db.predictions.insertMany([
  {comment_id:1, text_original:"Great service!", text_clean:"great service", prediction:"positivo", confidence:0.97, probabilities:{positivo:0.97,negativo:0.02,neutral:0.01}, ingested_at:new Date(), model_version:"v1.0.0"},
  {comment_id:2, text_original:"Terrible experience.", text_clean:"terrible experience", prediction:"negativo", confidence:0.95, probabilities:{positivo:0.02,negativo:0.95,neutral:0.03}, ingested_at:new Date(), model_version:"v1.0.0"},
  {comment_id:3, text_original:"It was okay.", text_clean:"it was okay", prediction:"neutral", confidence:0.78, probabilities:{positivo:0.11,negativo:0.11,neutral:0.78}, ingested_at:new Date(), model_version:"v1.0.0"}
]);
print("Seeded 3 sample predictions.");
'
