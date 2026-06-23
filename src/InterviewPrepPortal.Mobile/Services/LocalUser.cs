namespace InterviewPrepPortal.Mobile.Services;

/// <summary>
/// The mobile app has no login — it's a single-user app tied to the device.
/// Every call into IProgressService/ICustomAnswerService/INoteService uses this
/// fixed id as the "userId".
/// </summary>
public static class LocalUser
{
    public const string Id = "local";
}
