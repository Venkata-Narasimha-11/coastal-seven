import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  ShieldAlert,
  Package,
  PlusCircle,
  CheckCircle2,
  Truck,
  Check,
  AlertCircle,
  Image as ImageIcon,
  UploadCloud,
  Edit3,
  Trash2,
  RefreshCw,
  Bell,
  AlertTriangle,
  DollarSign,
  Boxes,
  Plus,
  ArrowRight,
  ArrowLeft,
  Eye,
  SlidersHorizontal,
  Sparkles,
  Layers,
  ChevronDown,
  Tag,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { useCart } from "../hooks/useCart";
import { orderService } from "../services/orderService";
import { productService } from "../services/productService";
import { productFormSchema } from "../schemas/productSchemas";
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from "../components/ui/table";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "../components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "../components/ui/dropdown-menu";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../components/ui/tabs";
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
import { Textarea } from "../components/ui/textarea";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { ImageDropzone } from "../components/ui/image-dropzone";
import { toast } from "../components/ui/sonner";

export const AdminPage = () => {
  const { user, isAdmin } = useAuth();
  const [activeTab, setActiveTab] = useState("orders");
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loadingOrders, setLoadingOrders] = useState(true);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [liveAlerts, setLiveAlerts] = useState([]);

  // Coupon Manager State (Feature 2)
  const { allCoupons, createCoupon, deleteCoupon } = useCart();
  const [newCouponCode, setNewCouponCode] = useState("");
  const [newDiscountType, setNewDiscountType] = useState("percentage");
  const [newDiscountValue, setNewDiscountValue] = useState("");
  const [newMinOrder, setNewMinOrder] = useState("");
  const [newExpiryDate, setNewExpiryDate] = useState("");
  const [newDescription, setNewDescription] = useState("");

  const handleAdminCreateCoupon = (e) => {
    e.preventDefault();
    if (!newCouponCode.trim()) {
      toast.error("Please provide a coupon code");
      return;
    }
    if (!newDiscountValue || Number(newDiscountValue) <= 0) {
      toast.error("Please provide a valid discount value");
      return;
    }
    if (!newExpiryDate) {
      toast.error("Please select an expiry date");
      return;
    }

    const code = newCouponCode.trim().toUpperCase();
    const typeLabel = newDiscountType === "percentage" ? `${newDiscountValue}%` : `$${newDiscountValue}`;
    createCoupon({
      code,
      discountType: newDiscountType,
      value: Number(newDiscountValue),
      minOrder: Number(newMinOrder) || 0,
      description: newDescription.trim() || `${typeLabel} Promotional Voucher`,
      expiryDate: newExpiryDate,
      terms: `Single-use per customer account. Min cart subtotal $${Number(newMinOrder || 0).toFixed(2)}.`,
    });

    toast.success(`Coupon "${code}" Created! 🎉`, {
      description: `Active immediately for all customers across the store.`,
    });

    setNewCouponCode("");
    setNewDiscountValue("");
    setNewMinOrder("");
    setNewExpiryDate("");
    setNewDescription("");
  };

  // Selected Order for Dialog modal
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [isOrderDialogOpen, setIsOrderDialogOpen] = useState(false);

  // Selected Product to delete
  const [productToDelete, setProductToDelete] = useState(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  // Product Creation Wizard: Steps (1: Details, 2: Stock & Specs, 3: Media Upload, 4: Preview)
  const [wizardStep, setWizardStep] = useState(1);
  const [uploadedImageFile, setUploadedImageFile] = useState(null);
  const [isPublishingProduct, setIsPublishingProduct] = useState(false);

  // React Hook Form with Zod validation + Dynamic Field Array
  const wizardForm = useForm({
    resolver: zodResolver(productFormSchema),
    defaultValues: {
      name: "",
      description: "",
      price: "",
      stock: "",
      category_id: "",
      is_active: true,
      specs: [
        { key: "Brand", value: "Guntur Store Exclusive" },
        { key: "Warranty", value: "1 Year Official" },
      ],
      tags: "new, featured, prime",
    },
    mode: "onTouched",
  });

  // Dynamic field array for product specifications
  const { fields: specFields, append: appendSpec, remove: removeSpec } = useFieldArray({
    control: wizardForm.control,
    name: "specs",
  });

  const fetchOrders = async () => {
    setLoadingOrders(true);
    try {
      const data = await orderService.getOrders();
      setOrders(data);
    } catch (err) {
      console.error("Failed to fetch admin orders:", err);
      toast.error("Failed to fetch orders");
    } finally {
      setLoadingOrders(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const cats = await productService.getCategories();
      setCategories(cats);
      if (cats.length > 0 && !wizardForm.getValues("category_id")) {
        wizardForm.setValue("category_id", cats[0].id);
      }
    } catch (err) {
      console.error("Failed to fetch categories:", err);
    }
  };

  const fetchProducts = async () => {
    setLoadingProducts(true);
    try {
      const res = await productService.getProducts({ size: 100 });
      setProducts(res.items || []);
    } catch (err) {
      console.error("Failed to fetch products:", err);
      toast.error("Failed to fetch catalog");
    } finally {
      setLoadingProducts(false);
    }
  };

  useEffect(() => {
    if (isAdmin) {
      fetchOrders();
      fetchCategories();
      fetchProducts();
    }
  }, [isAdmin]);

  // Real-time WebSocket connection to /ws/admin
  useEffect(() => {
    if (!isAdmin) return;
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/admin`;
    let socket;

    try {
      socket = new WebSocket(wsUrl);

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.event === "NEW_ORDER") {
            const newAlert = {
              id: Date.now(),
              type: "new_order",
              text: `🔔 New Order #${data.order_id} placed by ${data.customer} ($${data.total_amount})!`,
              time: new Date().toLocaleTimeString(),
            };

            if (data.out_of_stock && data.out_of_stock.length > 0) {
              const names = data.out_of_stock.map((p) => p.name).join(", ");
              const oosAlert = {
                id: Date.now() + 1,
                type: "out_of_stock",
                text: `🚨 CRITICAL ALERT: "${names}" is now OUT OF STOCK (Stock: 0)!`,
                time: new Date().toLocaleTimeString(),
              };
              setLiveAlerts((prev) => [oosAlert, newAlert, ...prev].slice(0, 10));
              toast.error("Stock Depleted!", { description: `"${names}" is now out of stock.` });
            } else {
              setLiveAlerts((prev) => [newAlert, ...prev].slice(0, 10));
              toast.success("New Order Incoming!", {
                description: `Order #${data.order_id} from ${data.customer}`,
              });
            }

            fetchOrders();
            fetchProducts();
          }
        } catch (e) {
          console.error("WS message parse error", e);
        }
      };
    } catch (e) {
      console.error("Admin WS connection error", e);
    }

    return () => {
      if (socket) socket.close();
    };
  }, [isAdmin]);

  // Status Change via DropdownMenu
  const handleStatusChange = async (orderId, newStatus) => {
    try {
      await orderService.updateOrderStatus(orderId, newStatus);
      toast.success("Status Updated", {
        description: `Order #${orderId} marked as ${newStatus.toUpperCase()}`,
      });
      fetchOrders();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to update order status");
    }
  };

  // Quick Restock Product
  const handleQuickRestock = async (productId, currentStock, addUnits = 10, productName = "") => {
    try {
      const newStock = Math.max(0, currentStock) + addUnits;
      await productService.updateProduct(productId, { stock: newStock });
      setProducts((prev) =>
        prev.map((p) => (p.id === productId ? { ...p, stock: newStock } : p))
      );
      toast.success("Stock Added", {
        description: `Restocked +${addUnits} for "${productName}". New stock: ${newStock}`,
      });
    } catch (err) {
      toast.error("Failed to restock product");
    }
  };

  // Confirm Delete Product via Dialog
  const confirmDeleteProduct = async () => {
    if (!productToDelete) return;
    try {
      await productService.deleteProduct(productToDelete.id);
      setProducts((prev) => prev.filter((p) => p.id !== productToDelete.id));
      toast.success("Product Deleted", {
        description: `"${productToDelete.name}" removed from catalog`,
      });
      setIsDeleteDialogOpen(false);
      setProductToDelete(null);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to delete product");
    }
  };

  // Step 1 -> Step 2 validation check
  const handleNextToStep2 = async () => {
    const valid = await wizardForm.trigger(["name", "description", "category_id"]);
    if (valid) setWizardStep(2);
  };

  // Step 2 -> Step 3 validation check
  const handleNextToStep3 = async () => {
    const valid = await wizardForm.trigger(["price", "stock", "specs"]);
    if (valid) setWizardStep(3);
  };

  // Step 3 -> Step 4 (Review)
  const handleNextToStep4 = () => {
    setWizardStep(4);
  };

  // Final Product Publication into FastAPI backend + Pillow image upload
  const handlePublishProduct = async (values) => {
    setIsPublishingProduct(true);
    try {
      // 1. Create product in DB
      const created = await productService.createProduct({
        name: values.name.trim(),
        description: values.description.trim(),
        price: parseFloat(values.price),
        stock: parseInt(values.stock, 10),
        category_id: parseInt(values.category_id, 10),
      });

      // 2. Upload file if dropped
      if (uploadedImageFile) {
        try {
          await productService.uploadProductImage(created.id, uploadedImageFile);
          toast.success("Image Processed", {
            description: "High-res & WebP thumbnails generated by Pillow",
          });
        } catch (imgErr) {
          console.error("Image upload warning:", imgErr);
        }
      }

      toast.success("Product Published Successfully! 🎉", {
        description: `"${created.name}" is now live in the storefront catalog.`,
      });

      // Reset wizard
      wizardForm.reset();
      setUploadedImageFile(null);
      setWizardStep(1);
      fetchProducts();
      setActiveTab("products");
    } catch (err) {
      console.error("Failed to publish product:", err);
      toast.error("Publication Failed", {
        description: err.response?.data?.detail || "Server error while saving product",
      });
    } finally {
      setIsPublishingProduct(false);
    }
  };

  const getStatusBadgeVariant = (status) => {
    switch (status) {
      case "delivered":
        return "success";
      case "shipped":
        return "info";
      case "processing":
        return "warning";
      case "cancelled":
        return "destructive";
      default:
        return "secondary";
    }
  };

  if (!isAdmin) {
    return (
      <Card className="max-w-md mx-auto my-12 text-center p-6 border-destructive/20 shadow-md">
        <CardHeader className="space-y-2">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-destructive/10 text-destructive">
            <ShieldAlert className="h-7 w-7" />
          </div>
          <CardTitle className="text-xl font-bold">Admin Privileges Required</CardTitle>
          <CardDescription>
            You are signed in as <strong>{user?.username || "a customer"}</strong> (role: {user?.role || "standard"}).
            This section is restricted to store administrators.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 pt-2">
          <p className="text-xs text-muted-foreground">
            To manage inventory, process orders, and launch new products with the Day 12 wizard, please sign in with an administrator account.
          </p>
          <div className="flex flex-col sm:flex-row gap-2 justify-center pt-2">
            <Link to="/">
              <Button variant="outline" size="sm" className="w-full sm:w-auto">
                Return to Storefront
              </Button>
            </Link>
            <Link to="/login">
              <Button size="sm" className="w-full sm:w-auto">
                Sign In as Admin
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-border/60">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Admin Operations Hub</h1>
            <Badge variant="warning" className="gap-1 font-semibold text-xs">
              <ShieldAlert className="h-3 w-3" /> Privileged
            </Badge>
          </div>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            Real-time management with Shadcn components, dynamic form specs & image previews
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              fetchOrders();
              fetchProducts();
              toast.info("Refreshed catalog and order records");
            }}
          >
            <RefreshCw className="h-3.5 w-3.5 mr-1.5" /> Refresh Live Data
          </Button>
          <Button size="sm" onClick={() => setActiveTab("new-product")}>
            <Plus className="h-3.5 w-3.5 mr-1.5" /> New Product Wizard
          </Button>
        </div>
      </div>

      {/* Real-time ticker banner if any alerts */}
      {liveAlerts.length > 0 && (
        <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-3 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2 font-medium text-amber-600 dark:text-amber-400">
            <Bell className="h-4 w-4 animate-bounce shrink-0" />
            <span>{liveAlerts[0].text}</span>
          </div>
          <Badge variant="outline" className="text-[10px] border-amber-500/30">
            {liveAlerts[0].time}
          </Badge>
        </div>
      )}

      {/* Shadcn Tabs Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-5 max-w-xl mb-6">
          <TabsTrigger value="orders" className="gap-1.5 text-xs">
            <Package className="h-3.5 w-3.5" />
            <span>Orders ({orders.length})</span>
          </TabsTrigger>
          <TabsTrigger value="products" className="gap-1.5 text-xs">
            <Boxes className="h-3.5 w-3.5" />
            <span>Products ({products.length})</span>
          </TabsTrigger>
          <TabsTrigger value="new-product" className="gap-1.5 text-xs">
            <PlusCircle className="h-3.5 w-3.5" />
            <span>Wizard</span>
          </TabsTrigger>
          <TabsTrigger value="coupons" className="gap-1.5 text-xs">
            <Tag className="h-3.5 w-3.5" />
            <span>Coupons</span>
          </TabsTrigger>
          <TabsTrigger value="alerts" className="gap-1.5 text-xs">
            <Bell className="h-3.5 w-3.5" />
            <span>Alerts ({liveAlerts.length})</span>
          </TabsTrigger>
        </TabsList>

        {/* ------------------------------------------------------------- */}
        {/* TAB 1: Live Orders Table with Shadcn Table & DropdownMenu */}
        {/* ------------------------------------------------------------- */}
        <TabsContent value="orders">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-bold flex items-center justify-between">
                <span>Customer Orders</span>
                <span className="text-xs font-normal text-muted-foreground">
                  Updated in real-time via WebSocket broadcast
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loadingOrders ? (
                <div className="flex justify-center py-12">
                  <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : orders.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground text-sm">
                  No orders recorded in database yet.
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Order #</TableHead>
                      <TableHead>Customer</TableHead>
                      <TableHead>Total Amount</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {orders.map((ord) => (
                      <TableRow key={ord.id}>
                        <TableCell className="font-bold text-primary">#{ord.id}</TableCell>
                        <TableCell>
                          <div className="font-medium text-xs text-foreground">
                            {ord.user?.username || `User #${ord.user_id}`}
                          </div>
                          <div className="text-[11px] text-muted-foreground truncate max-w-[180px]">
                            {ord.shipping_address || "Standard delivery"}
                          </div>
                        </TableCell>
                        <TableCell className="font-semibold text-xs">
                          ${Number(ord.total_amount || 0).toFixed(2)}
                        </TableCell>
                        <TableCell>
                          <Badge variant={getStatusBadgeVariant(ord.status)} className="capitalize text-xs">
                            {ord.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-xs text-muted-foreground">
                          {new Date(ord.created_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell className="text-right space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 text-xs"
                            onClick={() => {
                              setSelectedOrder(ord);
                              setIsOrderDialogOpen(true);
                            }}
                          >
                            <Eye className="h-3.5 w-3.5 mr-1" /> View
                          </Button>

                          {/* Shadcn DropdownMenu for Status Update */}
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="outline" size="sm" className="h-8 text-xs gap-1">
                                Status <ChevronDown className="h-3 w-3 opacity-60" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-40">
                              <DropdownMenuLabel className="text-xs">Set Status</DropdownMenuLabel>
                              <DropdownMenuSeparator />
                              {["pending", "processing", "shipped", "delivered", "cancelled"].map(
                                (st) => (
                                  <DropdownMenuItem
                                    key={st}
                                    onClick={() => handleStatusChange(ord.id, st)}
                                    className="capitalize text-xs cursor-pointer"
                                  >
                                    <span
                                      className={`inline-block w-2 h-2 rounded-full mr-2 ${
                                        st === "delivered"
                                          ? "bg-emerald-500"
                                          : st === "shipped"
                                          ? "bg-sky-500"
                                          : st === "processing"
                                          ? "bg-amber-500"
                                          : st === "cancelled"
                                          ? "bg-destructive"
                                          : "bg-muted-foreground"
                                      }`}
                                    />
                                    {st}
                                  </DropdownMenuItem>
                                )
                              )}
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ------------------------------------------------------------- */}
        {/* TAB 2: Live Products Table with Stock & Delete Dialog */}
        {/* ------------------------------------------------------------- */}
        <TabsContent value="products">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-bold flex items-center justify-between">
                <span>Product Catalog & Stock Controls</span>
                <span className="text-xs font-normal text-muted-foreground">
                  {products.length} live SKU records
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loadingProducts ? (
                <div className="flex justify-center py-12">
                  <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : products.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground text-sm">
                  No products in catalog. Launch the wizard to create one!
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Product</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Price</TableHead>
                      <TableHead>Stock Level</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {products.map((prod) => (
                      <TableRow key={prod.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="h-10 w-10 shrink-0 rounded-md border bg-muted/40 overflow-hidden flex items-center justify-center">
                              {prod.image_url ? (
                                <img
                                  src={prod.image_url}
                                  alt={prod.name}
                                  className="h-full w-full object-cover"
                                />
                              ) : (
                                <ImageIcon className="h-4 w-4 text-muted-foreground" />
                              )}
                            </div>
                            <div>
                              <p className="font-semibold text-xs text-foreground leading-tight">
                                {prod.name}
                              </p>
                              <p className="text-[11px] text-muted-foreground">ID: #{prod.id}</p>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="text-xs">
                          <Badge variant="outline">{prod.category?.name || "General"}</Badge>
                        </TableCell>
                        <TableCell className="font-semibold text-xs">
                          ${Number(prod.price || 0).toFixed(2)}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <span
                              className={`text-xs font-bold ${
                                prod.stock === 0
                                  ? "text-destructive"
                                  : prod.stock < 10
                                  ? "text-amber-500"
                                  : "text-emerald-600 dark:text-emerald-400"
                              }`}
                            >
                              {prod.stock} units
                            </span>
                            {prod.stock === 0 && (
                              <Badge variant="destructive" className="text-[10px] py-0">
                                Out of Stock
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell className="text-right space-x-1.5">
                          <Button
                            variant="outline"
                            size="sm"
                            className="h-7 text-xs border-emerald-500/30 text-emerald-600 hover:bg-emerald-500/10"
                            onClick={() => handleQuickRestock(prod.id, prod.stock, 10, prod.name)}
                          >
                            +10 Stock
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-7 w-7 text-destructive hover:bg-destructive/10"
                            onClick={() => {
                              setProductToDelete(prod);
                              setIsDeleteDialogOpen(true);
                            }}
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ------------------------------------------------------------- */}
        {/* TAB 3: Multi-Step Product Wizard with Dynamic Fields & Dropzone */}
        {/* ------------------------------------------------------------- */}
        <TabsContent value="new-product">
          <Card className="max-w-3xl mx-auto">
            <CardHeader className="pb-4 border-b">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg font-bold flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-primary" /> Product Creation Wizard
                  </CardTitle>
                  <CardDescription className="text-xs">
                    Multi-step form with dynamic specifications (`useFieldArray`) and drag-and-drop media upload
                  </CardDescription>
                </div>
                <Badge variant="secondary" className="text-xs font-medium">
                  Step {wizardStep} of 4
                </Badge>
              </div>

              {/* Mini step breadcrumb */}
              <div className="flex items-center gap-2 pt-3">
                {[
                  { n: 1, label: "Info" },
                  { n: 2, label: "Pricing & Specs" },
                  { n: 3, label: "Image Dropzone" },
                  { n: 4, label: "Review & Publish" },
                ].map((s) => (
                  <div
                    key={s.n}
                    className={`flex-1 h-1.5 rounded-full transition-colors ${
                      wizardStep >= s.n ? "bg-primary" : "bg-muted"
                    }`}
                    title={s.label}
                  />
                ))}
              </div>
            </CardHeader>

            <CardContent className="pt-6">
              <Form {...wizardForm}>
                <form
                  onSubmit={wizardForm.handleSubmit(handlePublishProduct)}
                  className="space-y-6"
                  noValidate
                >
                  {/* STEP 1: Basic Information */}
                  {wizardStep === 1 && (
                    <div className="space-y-4 animate-in fade-in-50">
                      <FormField
                        control={wizardForm.control}
                        name="name"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel required>Product Name</FormLabel>
                            <FormControl>
                              <Input
                                placeholder="e.g. Ultra Gaming Headset Pro"
                                autoFocus
                                {...field}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={wizardForm.control}
                        name="category_id"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel required>Category</FormLabel>
                            <FormControl>
                              <select
                                className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                {...field}
                              >
                                {categories.map((c) => (
                                  <option key={c.id} value={c.id}>
                                    {c.name}
                                  </option>
                                ))}
                              </select>
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={wizardForm.control}
                        name="description"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel required>Description</FormLabel>
                            <FormControl>
                              <Textarea
                                placeholder="Detailed overview of technical specifications, features, warranty, and package contents (min 10 characters)..."
                                className="min-h-[100px]"
                                {...field}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <div className="flex justify-end pt-4">
                        <Button type="button" onClick={handleNextToStep2}>
                          Continue to Pricing & Specs <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* STEP 2: Pricing, Stock, and Dynamic Specifications via useFieldArray */}
                  {wizardStep === 2 && (
                    <div className="space-y-6 animate-in fade-in-50">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <FormField
                          control={wizardForm.control}
                          name="price"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel required>Price ($ USD)</FormLabel>
                              <FormControl>
                                <Input type="number" step="0.01" placeholder="99.99" {...field} />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />

                        <FormField
                          control={wizardForm.control}
                          name="stock"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel required>Initial Stock Units</FormLabel>
                              <FormControl>
                                <Input type="number" step="1" placeholder="50" {...field} />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>

                      {/* DYNAMIC FORM FIELDS: useFieldArray */}
                      <div className="rounded-lg border border-border p-4 bg-muted/20 space-y-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-xs font-bold text-foreground flex items-center gap-1.5">
                              <SlidersHorizontal className="h-3.5 w-3.5 text-primary" />
                              Dynamic Product Attributes (useFieldArray)
                            </h4>
                            <p className="text-[11px] text-muted-foreground">
                              Add custom key-value specifications dynamically
                            </p>
                          </div>
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            className="h-7 text-xs"
                            onClick={() => appendSpec({ key: "", value: "" })}
                          >
                            <Plus className="h-3 w-3 mr-1" /> Add Spec
                          </Button>
                        </div>

                        {specFields.map((fieldItem, index) => (
                          <div key={fieldItem.id} className="flex items-center gap-2">
                            <FormField
                              control={wizardForm.control}
                              name={`specs.${index}.key`}
                              render={({ field }) => (
                                <FormItem className="flex-1">
                                  <FormControl>
                                    <Input placeholder="Attribute (e.g. Color)" {...field} />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />

                            <FormField
                              control={wizardForm.control}
                              name={`specs.${index}.value`}
                              render={({ field }) => (
                                <FormItem className="flex-1">
                                  <FormControl>
                                    <Input placeholder="Value (e.g. Matte Black)" {...field} />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />

                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="h-9 w-9 text-destructive hover:bg-destructive/10 shrink-0"
                              onClick={() => removeSpec(index)}
                              title="Delete attribute"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        ))}
                      </div>

                      <div className="flex items-center justify-between pt-4">
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => setWizardStep(1)}
                        >
                          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Details
                        </Button>
                        <Button type="button" onClick={handleNextToStep3}>
                          Continue to Media Upload <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* STEP 3: Drag-and-Drop Image Upload via react-dropzone */}
                  {wizardStep === 3 && (
                    <div className="space-y-4 animate-in fade-in-50">
                      <div>
                        <h4 className="text-sm font-semibold text-foreground">Product Image & Media</h4>
                        <p className="text-xs text-muted-foreground mt-0.5">
                          Drag and drop or select an image file with live preview
                        </p>
                      </div>

                      <ImageDropzone
                        value={uploadedImageFile}
                        onFileSelect={(file) => setUploadedImageFile(file)}
                        maxSize={5 * 1024 * 1024}
                      />

                      <div className="flex items-center justify-between pt-4">
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => setWizardStep(2)}
                        >
                          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Specs
                        </Button>
                        <Button type="button" onClick={handleNextToStep4}>
                          Review & Preview <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* STEP 4: Live Storefront Card Preview & Review */}
                  {wizardStep === 4 && (
                    <div className="space-y-6 animate-in fade-in-50">
                      <div className="rounded-lg border border-border p-4 bg-muted/20 space-y-4">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold uppercase text-primary">
                            Live Storefront Card Preview
                          </span>
                          <Badge variant="success">Ready to Publish</Badge>
                        </div>

                        {/* Interactive mockup card */}
                        <div className="max-w-xs mx-auto border rounded-xl bg-card overflow-hidden shadow-sm">
                          <div className="h-44 bg-muted/40 flex items-center justify-center overflow-hidden">
                            {uploadedImageFile ? (
                              <img
                                src={URL.createObjectURL(uploadedImageFile)}
                                alt="Preview"
                                className="h-full w-full object-contain"
                              />
                            ) : (
                              <ImageIcon className="h-8 w-8 text-muted-foreground" />
                            )}
                          </div>
                          <div className="p-4 space-y-2">
                            <span className="text-[10px] font-semibold uppercase text-muted-foreground">
                              {categories.find((c) => c.id == wizardForm.getValues("category_id"))
                                ?.name || "General"}
                            </span>
                            <h5 className="font-bold text-sm text-foreground line-clamp-1">
                              {wizardForm.getValues("name") || "Untitled Product"}
                            </h5>
                            <p className="text-xs text-muted-foreground line-clamp-2">
                              {wizardForm.getValues("description")}
                            </p>
                            <div className="flex items-center justify-between pt-2 border-t text-sm font-bold text-foreground">
                              <span>${Number(wizardForm.getValues("price") || 0).toFixed(2)}</span>
                              <Badge variant="outline" className="text-[11px]">
                                {wizardForm.getValues("stock") || 0} in stock
                              </Badge>
                            </div>
                          </div>
                        </div>

                        {/* Specs summary */}
                        {wizardForm.getValues("specs")?.length > 0 && (
                          <div className="text-xs space-y-1 border-t pt-3">
                            <span className="font-semibold text-muted-foreground">
                              Attached Specifications:
                            </span>
                            <div className="flex flex-wrap gap-1.5 pt-1">
                              {wizardForm.getValues("specs").map((sp, idx) => (
                                <Badge key={idx} variant="secondary" className="text-[11px]">
                                  {sp.key}: {sp.value}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center justify-between pt-4">
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => setWizardStep(3)}
                          disabled={isPublishingProduct}
                        >
                          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Upload
                        </Button>
                        <Button
                          type="submit"
                          className="bg-emerald-600 hover:bg-emerald-700 text-white min-w-[170px]"
                          isLoading={isPublishingProduct}
                          disabled={isPublishingProduct}
                        >
                          <CheckCircle2 className="mr-2 h-4 w-4" />
                          {isPublishingProduct ? "Publishing..." : "Publish to Catalog"}
                        </Button>
                      </div>
                    </div>
                  )}
                </form>
              </Form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ------------------------------------------------------------- */}
        {/* TAB 4: WebSocket Alerts Log */}
        {/* ------------------------------------------------------------- */}
        <TabsContent value="alerts">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-bold flex items-center justify-between">
                <span>Real-Time Broadcast Event Log</span>
                <Badge variant="outline" className="text-xs">
                  WebSocket /ws/admin
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {liveAlerts.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground text-sm">
                  Listening for order placements and inventory alerts...
                </div>
              ) : (
                <div className="space-y-2">
                  {liveAlerts.map((a) => (
                    <div
                      key={a.id}
                      className={`flex items-center justify-between p-3 rounded-lg border text-xs ${
                        a.type === "out_of_stock"
                          ? "border-destructive/40 bg-destructive/10 text-destructive font-semibold"
                          : "border-border bg-card text-foreground"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        {a.type === "out_of_stock" ? (
                          <AlertTriangle className="h-4 w-4 shrink-0 text-destructive" />
                        ) : (
                          <Bell className="h-4 w-4 shrink-0 text-primary" />
                        )}
                        <span>{a.text}</span>
                      </div>
                      <span className="text-[11px] text-muted-foreground">{a.time}</span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ------------------------------------------------------------- */}
        {/* TAB 5: Dynamic Coupon Creator & Manager (Feature 2) */}
        {/* ------------------------------------------------------------- */}
        <TabsContent value="coupons" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Create Coupon Form Card */}
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="text-base font-bold flex items-center gap-2">
                  <Tag className="h-4 w-4 text-primary" />
                  <span>Create Promo Coupon</span>
                </CardTitle>
                <CardDescription className="text-xs">
                  Issue storewide promotional codes with minimum spend thresholds and expiry dates.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleAdminCreateCoupon} className="space-y-3.5 text-xs">
                  <div>
                    <label className="font-semibold block mb-1">Coupon Code</label>
                    <Input
                      type="text"
                      placeholder="e.g. DIWALI30"
                      value={newCouponCode}
                      onChange={(e) => setNewCouponCode(e.target.value.toUpperCase())}
                      className="uppercase font-mono"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="font-semibold block mb-1">Discount Type</label>
                      <select
                        className="input w-full p-2 text-xs"
                        value={newDiscountType}
                        onChange={(e) => setNewDiscountType(e.target.value)}
                      >
                        <option value="percentage">Percentage (%)</option>
                        <option value="flat">Flat Amount ($)</option>
                      </select>
                    </div>
                    <div>
                      <label className="font-semibold block mb-1">
                        {newDiscountType === "percentage" ? "Discount %" : "Discount ($)"}
                      </label>
                      <Input
                        type="number"
                        min="1"
                        max={newDiscountType === "percentage" ? "99" : "10000"}
                        placeholder={newDiscountType === "percentage" ? "25" : "50"}
                        value={newDiscountValue}
                        onChange={(e) => setNewDiscountValue(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="font-semibold block mb-1">Min Order ($)</label>
                      <Input
                        type="number"
                        min="0"
                        placeholder="50"
                        value={newMinOrder}
                        onChange={(e) => setNewMinOrder(e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="font-semibold block mb-1">Expiry Date</label>
                      <Input
                        type="date"
                        value={newExpiryDate}
                        onChange={(e) => setNewExpiryDate(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="font-semibold block mb-1">Description</label>
                    <Input
                      type="text"
                      placeholder="e.g. 25% Grand Festive Offer on Laptops"
                      value={newDescription}
                      onChange={(e) => setNewDescription(e.target.value)}
                    />
                  </div>

                  <Button type="submit" className="w-full gap-2 font-bold mt-2">
                    <Plus className="h-4 w-4" /> Issue Store Coupon
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Active Coupons List Card */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-base font-bold flex items-center justify-between">
                  <span>Store Promotional Offers ({Object.keys(allCoupons || {}).length})</span>
                  <Badge variant="outline" className="text-xs">Amazon 1-Use Policy Enforced</Badge>
                </CardTitle>
                <CardDescription className="text-xs">
                  Active promotional vouchers available for redemption during checkout.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="rounded-md border overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Code</TableHead>
                        <TableHead>Discount</TableHead>
                        <TableHead>Min Order</TableHead>
                        <TableHead>Expires</TableHead>
                        <TableHead>Terms</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {Object.values(allCoupons || {}).map((coupon) => {
                        const isExpired = new Date().toISOString().split("T")[0] > coupon.expiryDate;
                        const isSystem = ["FESTIVE10", "SAVE20", "GUNTUR50", "AMAZON50"].includes(coupon.code);

                        return (
                          <TableRow key={coupon.code}>
                            <TableCell className="font-mono font-bold text-primary">
                              {coupon.code}
                            </TableCell>
                            <TableCell>
                              <Badge variant={coupon.discountType === "percentage" ? "default" : "secondary"}>
                                {coupon.discountType === "percentage" ? `${coupon.value}% OFF` : `$${coupon.value} Flat`}
                              </Badge>
                            </TableCell>
                            <TableCell className="text-xs font-semibold">
                              ${Number(coupon.minOrder || 0).toFixed(2)}
                            </TableCell>
                            <TableCell className="text-xs">
                              <span className={isExpired ? "text-destructive font-bold" : "text-muted-foreground"}>
                                {coupon.expiryDate} {isExpired && "(Expired)"}
                              </span>
                            </TableCell>
                            <TableCell className="text-[11px] text-muted-foreground max-w-[180px] truncate" title={coupon.description}>
                              {coupon.description}
                            </TableCell>
                            <TableCell className="text-right">
                              {isSystem ? (
                                <Badge variant="outline" className="text-[10px]">Default</Badge>
                              ) : (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-7 w-7 p-0 text-destructive hover:bg-destructive/10"
                                  onClick={() => {
                                    deleteCoupon(coupon.code);
                                    toast.info(`Coupon "${coupon.code}" deleted`);
                                  }}
                                  title="Delete custom coupon"
                                >
                                  <Trash2 className="h-3.5 w-3.5" />
                                </Button>
                              )}
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* ------------------------------------------------------------- */}
      {/* SHADCN DIALOG: Order Details Modal */}
      {/* ------------------------------------------------------------- */}
      <Dialog open={isOrderDialogOpen} onOpenChange={setIsOrderDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="text-lg font-bold">
              Order #{selectedOrder?.id} Details
            </DialogTitle>
            <DialogDescription className="text-xs">
              Recorded on {selectedOrder && new Date(selectedOrder.created_at).toLocaleString()}
            </DialogDescription>
          </DialogHeader>

          {selectedOrder && (
            <div className="space-y-4 py-2 text-xs">
              <div className="flex justify-between border-b pb-2">
                <span className="text-muted-foreground">Customer:</span>
                <span className="font-semibold text-foreground">
                  {selectedOrder.user?.username || `User #${selectedOrder.user_id}`}
                </span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="text-muted-foreground">Status:</span>
                <Badge variant={getStatusBadgeVariant(selectedOrder.status)} className="capitalize text-[11px]">
                  {selectedOrder.status}
                </Badge>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="text-muted-foreground">Total Paid:</span>
                <span className="font-bold text-primary text-sm">
                  ${Number(selectedOrder.total_amount || 0).toFixed(2)}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground block mb-1">Shipping Destination:</span>
                <p className="rounded bg-muted/40 p-2 text-[11px] text-foreground font-mono">
                  {selectedOrder.shipping_address}
                </p>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setIsOrderDialogOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ------------------------------------------------------------- */}
      {/* SHADCN DIALOG: Delete Product Confirmation Modal */}
      {/* ------------------------------------------------------------- */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle className="text-destructive flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" /> Delete Product?
            </DialogTitle>
            <DialogDescription className="text-xs">
              Are you sure you want to remove <strong>"{productToDelete?.name}"</strong>? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2 sm:gap-0">
            <Button variant="outline" size="sm" onClick={() => setIsDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" size="sm" onClick={confirmDeleteProduct}>
              Yes, Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminPage;
