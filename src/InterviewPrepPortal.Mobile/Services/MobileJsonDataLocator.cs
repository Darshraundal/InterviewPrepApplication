using InterviewPrepPortal.Interfaces;

namespace InterviewPrepPortal.Mobile.Services;

/// <summary>
/// Points the shared QuestionService/ProjectGuideService at the app-local folder
/// that bundled JSON assets get extracted to on first launch (see JsonDataSeeder).
/// </summary>
public class MobileJsonDataLocator : IJsonDataLocator
{
    public string JsonDataRoot => Path.Combine(FileSystem.AppDataDirectory, "jsondata");
}
