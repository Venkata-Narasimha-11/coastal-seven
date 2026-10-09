import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { UserPlus, ShieldAlert, Sparkles, CheckCircle2, Eye, EyeOff } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { registerSchema } from "../schemas/authSchemas";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "../components/ui/card";
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
} from "../components/ui/form";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { toast } from "../components/ui/sonner";

export const RegisterPage = () => {
  const { register: authRegister, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [serverError, setServerError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const searchParams = new URLSearchParams(location.search);
  const redirectParam = searchParams.get("redirect") || "/";

  const form = useForm({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      username: "",
      email: "",
      full_name: "",
      password: "",
      confirmPassword: "",
    },
    mode: "onTouched",
  });

  const { isSubmitting } = form.formState;

  const onSubmit = async (values) => {
    setServerError("");
    try {
      await authRegister({
        username: values.username.trim(),
        email: values.email.trim(),
        full_name: values.full_name?.trim() || undefined,
        password: values.password,
      });

      toast.success("Account created successfully!", {
        description: "Signing you in automatically...",
      });

      // Auto login after registration
      await login(values.username.trim(), values.password);
      navigate(redirectParam);
    } catch (err) {
      console.error("Registration error:", err);
      const message =
        err.response?.data?.detail || "Registration failed. Please check inputs and try again.";
      setServerError(message);
      toast.error("Registration Failed", {
        description: message,
      });
    }
  };

  const autofillDemo = () => {
    const randomSuffix = Math.floor(Math.random() * 900) + 100;
    form.setValue("username", `user_${randomSuffix}`, { shouldValidate: true, shouldDirty: true });
    form.setValue("email", `shopper_${randomSuffix}@example.com`, { shouldValidate: true, shouldDirty: true });
    form.setValue("full_name", `Shopper Demo ${randomSuffix}`, { shouldValidate: true, shouldDirty: true });
    form.setValue("password", "Passcode123!", { shouldValidate: true, shouldDirty: true });
    form.setValue("confirmPassword", "Passcode123!", { shouldValidate: true, shouldDirty: true });
    setServerError("");
  };

  return (
    <div className="flex min-h-[85vh] items-center justify-center px-4 py-8">
      <Card className="w-full max-w-lg shadow-lg border-border/80 bg-card">
        <CardHeader className="space-y-2 text-center pb-6">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
            <UserPlus className="h-6 w-6 stroke-[2]" />
          </div>
          <CardTitle className="text-2xl font-bold tracking-tight">
            Create an Account
          </CardTitle>
          <CardDescription className="text-xs sm:text-sm">
            Join the store with strict Zod schema validation & client security
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Quick Demo Fill */}
          <div className="rounded-lg border border-dashed border-border/80 bg-muted/40 p-3 text-xs flex items-center justify-between">
            <span className="flex items-center gap-1.5 font-medium text-muted-foreground">
              <Sparkles className="h-3.5 w-3.5 text-primary" /> Test Account Generator
            </span>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="h-7 text-xs border-primary/30 text-primary hover:bg-primary/10"
              onClick={autofillDemo}
            >
              Fill Sample User
            </Button>
          </div>

          {serverError && (
            <div
              className="flex items-center gap-2 rounded-lg bg-destructive/10 p-3 text-xs font-medium text-destructive border border-destructive/20 animate-in fade-in-50"
              role="alert"
            >
              <ShieldAlert className="h-4 w-4 shrink-0" />
              <span>{serverError}</span>
            </div>
          )}

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4" noValidate>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="username"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Username *</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="e.g. alex_coder"
                          autoComplete="username"
                          autoFocus
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email Address *</FormLabel>
                      <FormControl>
                        <Input
                          type="email"
                          placeholder="alex@domain.com"
                          autoComplete="email"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="full_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Full Legal Name</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Alex Morgan (Optional)"
                        autoComplete="name"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription className="text-[11px]">
                      Used for delivery recipient identification
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Password *</FormLabel>
                      <FormControl>
                        <div className="relative">
                          <Input
                            type={showPassword ? "text" : "password"}
                            placeholder="Min 8 chars (letters + numbers)"
                            autoComplete="new-password"
                            className="pr-9"
                            {...field}
                          />
                          <button
                            type="button"
                            className="absolute right-3 top-2.5 text-muted-foreground hover:text-foreground"
                            onClick={() => setShowPassword(!showPassword)}
                            aria-label={showPassword ? "Hide password" : "Show password"}
                          >
                            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </button>
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="confirmPassword"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Confirm Password *</FormLabel>
                      <FormControl>
                        <Input
                          type={showPassword ? "text" : "password"}
                          placeholder="Repeat password"
                          autoComplete="new-password"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <Button
                type="submit"
                className="w-full font-medium"
                disabled={isSubmitting}
                loading={isSubmitting}
              >
                <UserPlus className="mr-2 h-4 w-4" />
                {isSubmitting ? "Creating Account..." : "Register & Sign In"}
              </Button>
            </form>
          </Form>
        </CardContent>

        <CardFooter className="flex flex-col space-y-3 pt-2 text-center text-xs text-muted-foreground border-t border-border/50">
          <div className="flex items-center justify-center gap-1.5">
            <span>Already registered?</span>
            <Link
              to={`/login${redirectParam ? `?redirect=${encodeURIComponent(redirectParam)}` : ""}`}
              className="font-semibold text-primary hover:underline"
            >
              Sign In Instead
            </Link>
          </div>
          <div className="flex items-center justify-center gap-1 text-[11px] text-muted-foreground/80">
            <CheckCircle2 className="h-3 w-3 text-emerald-500" />
            <span>FastAPI JWT Bearer Authentication Active</span>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
};

export default RegisterPage;
