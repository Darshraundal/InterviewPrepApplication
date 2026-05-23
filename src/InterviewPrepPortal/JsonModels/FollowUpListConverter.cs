using System.Text.Json;
using System.Text.Json.Serialization;

namespace InterviewPrepPortal.JsonModels;

/// <summary>
/// Handles two historical JSON shapes for the "followUps" array:
///
///   NEW (current)  – array of objects with "question"/"answer" fields:
///       "followUps": [{ "question": "...", "answer": "..." }]
///
///   OLD (legacy)   – array of plain strings (answers lived in "followUpAnswers"):
///       "followUps": ["What is X?", "What is Y?"]
///
/// When the old format is encountered the converter produces FollowUp objects
/// with the question text set and an empty answer. The answer is never shown
/// to the user from that path because the legacy "followUpAnswers" dict is
/// also present on the Question and can be used as a fallback by the view.
/// </summary>
public sealed class FollowUpListConverter : JsonConverter<List<FollowUp>>
{
    public override List<FollowUp> Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        var result = new List<FollowUp>();

        if (reader.TokenType != JsonTokenType.StartArray)
            throw new JsonException("Expected start of array for followUps.");

        while (reader.Read())
        {
            if (reader.TokenType == JsonTokenType.EndArray)
                return result;

            if (reader.TokenType == JsonTokenType.String)
            {
                // OLD format — plain string question, no inline answer
                result.Add(new FollowUp { Question = reader.GetString() ?? string.Empty });
            }
            else if (reader.TokenType == JsonTokenType.StartObject)
            {
                // NEW format — object with question + answer fields
                var followUp = new FollowUp();
                while (reader.Read() && reader.TokenType != JsonTokenType.EndObject)
                {
                    if (reader.TokenType != JsonTokenType.PropertyName) continue;
                    var propName = reader.GetString();
                    reader.Read();
                    if (propName?.Equals("question", StringComparison.OrdinalIgnoreCase) == true)
                        followUp.Question = reader.GetString() ?? string.Empty;
                    else if (propName?.Equals("answer", StringComparison.OrdinalIgnoreCase) == true)
                        followUp.Answer = reader.GetString() ?? string.Empty;
                    // skip unknown properties
                }
                result.Add(followUp);
            }
            else
            {
                reader.Skip();
            }
        }

        return result;
    }

    public override void Write(Utf8JsonWriter writer, List<FollowUp> value, JsonSerializerOptions options)
    {
        writer.WriteStartArray();
        foreach (var fu in value)
        {
            writer.WriteStartObject();
            writer.WriteString("question", fu.Question);
            writer.WriteString("answer", fu.Answer);
            writer.WriteEndObject();
        }
        writer.WriteEndArray();
    }
}
